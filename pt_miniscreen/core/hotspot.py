import logging
import threading
from time import sleep, time
from typing import Any, Dict
from weakref import WeakMethod

from PIL import Image

from .utils import is_same_image

logger = logging.getLogger(__name__)


class Interval(threading.Timer):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.daemon = True

    @property
    def function(self):
        return self._get_function()

    @function.setter
    def function(self, next_value):
        self._get_function = WeakMethod(next_value)

    def run(self):
        execution_time = 0

        while not self.finished.is_set():
            wait_time = self.interval - execution_time
            if wait_time < 0:
                logger.warning(f"Interval lagging by {-wait_time}s")

            sleep(max(wait_time, 0))

            # stop interval if parent has been garbage collected
            if self.function is None:
                return

            start_time = time()
            self.function(*self.args, **self.kwargs)
            execution_time = start_time - time()


class State(dict):
    def __init__(self, initial_state, on_state_update):
        self._get_on_state_update = WeakMethod(on_state_update)
        super().__init__(initial_state)

    def update(self, *args, **kwargs):
        previous_state = self.copy()
        super().update(*args, **kwargs)
        on_state_update = self._get_on_state_update()
        if callable(on_state_update):
            on_state_update(previous_state)


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


class Hotspot:
    default_state: Dict[Any, Any] = {}

    def __del__(self):
        logger.debug(f"Garbage collect {self}")
        self._cleanup()

    def __init__(self, on_rerender, initial_state={}):
        self._hotspots = []
        self._intervals = []
        self._render_cache = RenderCache()
        self._get_on_rerender = WeakMethod(on_rerender)
        self.state = State(
            initial_state={**self.default_state, **initial_state},
            on_state_update=self._on_state_update,
        )

        # wrap subclass render method to track image properties and optimise
        self._unmodified_render = self.render

        def render(image):
            # set size of hotspot to input image for use in calculations
            self.size = image.size
            self.width = image.width
            self.height = image.height

            # return cached output if input is the same
            if is_same_image(image, self._render_cache.input):
                return self._render_cache.output

            logger.debug(f"{self} rendering")
            self._render_cache.input = image
            output = self._unmodified_render(image.copy())
            self._render_cache.output = output
            return output

        self.render = render

    def _reconcile(self):
        # bail if parent no longer exists
        on_rerender = self._get_on_rerender()
        if not callable(on_rerender):
            return

        # if render has never been called always notify parent about rerender
        if not isinstance(self._render_cache.input, Image.Image):
            return on_rerender()

        # do nothing if render output is unchanged
        render_output = self._unmodified_render(self._render_cache.input)
        if is_same_image(render_output, self._render_cache.output):
            return

        # cache the new output and notify parent about the rerender
        self._render_cache.output = render_output
        on_rerender()

    def _cleanup(self):
        # stop notifying parent of updates immediately
        self._get_on_rerender = lambda: None

        for interval in self._intervals:
            interval.cancel()

        for hotspot in self._hotspots:
            hotspot._cleanup()

        self._intervals = []
        self._hotspots = []

        # subclass specific cleanup
        self.cleanup()

    def _on_state_update(self, previous_state):
        if self.state != previous_state:
            self.on_state_change(previous_state)
            self._reconcile()

    # lifecycle hooks
    def cleanup(self):
        pass

    def on_state_change(self, previous_state):
        pass

    # external API
    def create_hotspot(self, ChildHotspot, **kwargs):
        hotspot = ChildHotspot(**kwargs, on_rerender=self._reconcile)
        self._hotspots.append(hotspot)
        return hotspot

    def create_interval(self, callback, timeout=1):
        interval = Interval(timeout, callback)
        interval.start()
        self._intervals.append(interval)
        return interval

    def remove_hotspot(self, hotspot):
        if hotspot not in self._hotspots:
            logger.warning(f"{self} tried to remove hotspot it doesn't own {hotspot}")
            return

        hotspot._cleanup()
        self._hotspots.remove(hotspot)

    def remove_interval(self, interval):
        if interval not in self._intervals:
            logger.warning(f"{self} tried to remove interval it doesn't own {interval}")
            return

        interval.cancel()
        self._intervals.remove(interval)

    def render(self, image: Image.Image):
        raise NotImplementedError("Hotspot subclasses must implement the render method")
