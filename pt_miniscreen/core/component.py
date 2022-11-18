import logging
import threading
from time import sleep, time
from typing import Any, Dict
from weakref import WeakMethod, ref

from PIL import Image

from .utils import is_same_image

logger = logging.getLogger(__name__)


class CreateComponentException(Exception):
    pass


class RenderException(Exception):
    pass


class StateAccessException(Exception):
    pass


# Inherit from Timer so that Interval shares the same API
class Interval(threading.Timer):
    def __init__(
        self,
        *args,
        active_event=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.get_active_event = ref(active_event)
        self.daemon = True  # Intervals shouldn't keep the process alive

    @property
    def function(self):
        return self._get_function()

    @function.setter
    def function(self, next_value):
        # Use a WeakMethod to store the function so that the Interval does not
        # produce a circular reference with the Component that created it which
        # would result in memory leaks.
        self._get_function = WeakMethod(next_value)

    # override run to execute function every `interval` seconds
    def run(self):
        execution_time = 0

        while True:
            # wait for active event to be set before continuing
            active_event = self.get_active_event()
            if isinstance(active_event, threading.Event):
                active_event.wait()

            # take execution time into account when waiting to produce a more
            # accurate interval time
            wait_time = self.interval - execution_time
            if wait_time < 0:
                logger.warning(f"Interval lagging by {-wait_time}s")

            sleep(max(wait_time, 0))

            # stop interval if cancel called or if parent has been cleaned up
            if self.finished.is_set() or self.function is None:
                return

            start_time = time()
            self.function(*self.args, **self.kwargs)
            execution_time = start_time - time()


class State(dict):
    def __repr__(self) -> str:
        return dict.__repr__(self.copy())

    def __eq__(self, other) -> bool:
        return dict.__eq__(self.copy(), other)

    def __init__(self, initial_state, on_state_update):
        # Use a WeakMethod to store on_state_update so that State does not
        # produce a circular reference with the Component that created it which
        # would result in memory leaks.
        self._get_on_state_update = WeakMethod(on_state_update)
        super().__init__(initial_state)

    def update(self, *args, **kwargs):
        previous_state = self.copy()
        super().update(*args, **kwargs)
        on_state_update = self._get_on_state_update()
        if callable(on_state_update):
            on_state_update(previous_state)


# Always create and return copies to prevent accidentally mutating the cache
class RenderCache:
    def __init__(self):
        self._input = {"copy": lambda: None}
        self._output = {"copy": lambda: None}

    @property
    def input(self):
        return self._input.copy()

    @input.setter
    def input(self, next_input):
        self._input = next_input.copy()

    @property
    def output(self):
        return self._output.copy()

    @output.setter
    def output(self, next_output):
        self._output = next_output.copy()


class Component:
    default_state: Dict[Any, Any] = {}

    def __del__(self):
        logger.debug(f"Garbage collect {self}")
        self._cleanup()

    def __init__(self, on_rerender=None, initial_state={}):
        if on_rerender is None:
            raise CreateComponentException(
                "Component must be created with create_child method. This error might be because kwargs not passed to super in component init method."
            )

        self._children = []
        self._intervals = []
        self._render_cache = RenderCache()
        self._get_on_rerender = WeakMethod(on_rerender)
        self._state = State(
            initial_state={**self.default_state, **initial_state},
            on_state_update=self._on_state_update,
        )
        self._reconciliation_lock = threading.Lock()
        self._reconciliation_queued = False

        self.active_event = threading.Event()
        self.mounted = False
        self.rendered = False
        self.width = None
        self.height = None
        self.size = None

        # replace subclass render method to add custom behaviour
        self._original_render = self.render
        self.render = self._render

    def _cleanup(self):
        # stop notifying parent of updates immediately
        self._get_on_rerender = lambda: None

        # subclass specific cleanup
        self.cleanup()

        if hasattr(self, "_intervals"):
            for interval in self._intervals:
                interval.cancel()

            self._intervals = []

        if hasattr(self, "_children"):
            for child in self._children:
                child._cleanup()

            self._children = []

        # set active_event so that threads that are waiting are cleaned up
        if hasattr(self, "active_event"):
            self.active_event.set()

    def _set_active(self, active):
        if active:
            self.active_event.set()
        else:
            self.active_event.clear()

        # also set children to have the correct active state
        for child in self._children:
            child._set_active(active and child.rendered)

    def _internal_render(self, image):
        # mark children as not rendered, when original render is called the ones
        # that have their render methods called will switch it back to True.
        for child in self._children:
            child.rendered = False

        output = self._original_render(image)

        # set children that were rendered to active, otherwise pause them
        # if self is not rendered all children should be paused
        for child in self._children:
            child._set_active(self.rendered and child.rendered)

        return output

    def _render(self, image):
        if image.height == 0 or image.width == 0:
            raise RenderException(
                "Image passed to render must have non-zero height and width"
            )

        # set size of component to input image for use in calculations
        self.size = image.size
        self.width = image.width
        self.height = image.height

        # mark component as rendered
        self.rendered = True

        # return cached output if input is the same
        if is_same_image(image, self._render_cache.input):
            return self._render_cache.output

        logger.debug(f"{self} rendering")
        self._render_cache.input = image
        output = self._internal_render(self._render_cache.input)

        if not isinstance(output, Image.Image):
            raise RenderException(
                f"Pillow Image must be returned from render, returned {output}"
            )

        if image.size != output.size:
            raise RenderException(
                f"Image returned from render must be same size as the passed image: passed {image.size}, returned {output.size}"
            )

        self._render_cache.output = output

        # mark the component as mounted once the render cache is populated
        self.mounted = True

        return output

    def _on_state_update(self, previous_state):
        if self.state != previous_state:
            self.on_state_change(previous_state)

            if self.mounted:
                self._reconcile()

    def _reconcile(self):
        if self._reconciliation_queued:
            # since state is always up-to-date we can let the queued reconcile
            # handle the rerender and ignore this one. This prevents the queue
            # building up with very rapid updates
            return

        try:
            self._reconciliation_queued = self._reconciliation_lock.locked()
            self._reconciliation_lock.acquire()

            # do nothing if parent no longer exists
            on_rerender = self._get_on_rerender()
            if not callable(on_rerender):
                return

            # do nothing if component has never been rendered
            if not self.mounted:
                return

            render_output = self._internal_render(self._render_cache.input)

            # do nothing if render output is unchanged
            if is_same_image(render_output, self._render_cache.output):
                return

            # cache the new output and notify parent about the rerender
            self._render_cache.output = render_output
            on_rerender()

        finally:
            self._reconciliation_queued = False
            self._reconciliation_lock.release()

    # lifecycle hooks
    def cleanup(self):
        pass

    def on_state_change(self, previous_state):
        pass

    # external API
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        raise AttributeError(
            "Component.state cannot be set, pass initial_state to super().__init__ or call self.state.update"
        )

    def create_child(self, ChildComponent, **kwargs):
        child = ChildComponent(**kwargs, on_rerender=self._reconcile)
        self._children.append(child)
        return child

    def create_interval(self, callback, timeout=1):
        interval = Interval(timeout, callback, active_event=self.active_event)
        interval.start()
        self._intervals.append(interval)
        return interval

    def remove_child(self, child):
        if child not in self._children:
            logger.warning(f"{self} tried to remove unknown child: {child}")
            return

        child._cleanup()
        self._children.remove(child)

    def remove_interval(self, interval):
        if interval not in self._intervals:
            logger.warning(f"{self} tried to remove interval it doesn't own {interval}")
            return

        interval.cancel()
        self._intervals.remove(interval)

    def render(self, image: Image.Image):
        raise NotImplementedError(
            "Component subclasses must implement the render method"
        )
