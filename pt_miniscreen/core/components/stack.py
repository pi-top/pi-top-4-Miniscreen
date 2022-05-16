import logging
import threading

from ..component import Component
from ..utils import transition

logger = logging.getLogger(__name__)


class Stack(Component):
    transition_duration = 0.25
    width = 0
    default_state = {
        "x_position": 0,
        "stack": [],
        "active_transition": None,
    }

    def cleanup(self):
        self._cleanup_transition.set()

    def __init__(self, initial_stack=[], **kwargs):
        super().__init__(**kwargs)

        self._cleanup_transition = threading.Event()

        # setup initial stack
        self.state["stack"] = [
            self.create_child(Component) for Component in initial_stack
        ]

    @property
    def active_component(self):
        try:
            # when popping the top component is being removed and so isn't active
            if self.state["active_transition"] == "POP":
                return self.state["stack"][-2]

            # active component is the top item
            return self.state["stack"][-1]

        # if index out of range return None
        except IndexError:
            return None

    @property
    def active_index(self):
        try:
            return self.state["stack"].index(self.active_component)

        # if active_component not in stack return None
        except ValueError:
            return None

    @property
    def stack(self):
        return self.state["stack"]

    def _push_transition(self):
        # only animate transition if we know our width
        if self.width:
            for step in transition(self.width, self.transition_duration):
                if self._cleanup_transition.is_set():
                    return

                self.state.update(
                    {"x_position": min(self.width, self.state["x_position"] - step)}
                )

        self.state.update({"active_transition": None})

    def _pop_transition(self):
        # only animate transition if we know our width
        if self.width:
            for step in transition(self.width, self.transition_duration):
                if self._cleanup_transition.is_set():
                    return

                self.state.update(
                    {"x_position": min(self.width, self.state["x_position"] + step)}
                )

        stack = self.state["stack"]
        self.remove_child(stack.pop())
        self.state.update({"stack": stack, "active_transition": None})

    def push(self, Component, animate_transition=True):
        if self.state["active_transition"] is not None:
            logger.debug(f"Currently transitioning, ignoring push of {Component}")
            return

        logger.debug(f"Starting a new push transition with component {Component}")
        state_update = {
            "x_position": self.width or 0,  # use 0 if self.width is None
            "stack": self.state["stack"] + [self.create_child(Component)],
        }
        if animate_transition:
            state_update.update({"active_transition": "PUSH"})
        self.state.update(state_update)

        threading.Thread(target=self._push_transition).start()

    def pop(self, animate_transition=True):
        if self.state["active_transition"] is not None:
            logger.debug("Currently transitioning, ignoring pop")
            return

        if len(self.state["stack"]) == 0:
            logger.debug("Unable to pop since stack is empty, ignoring pop")
            return

        logger.debug("Starting a new pop transition")

        state_update = {"x_position": 0}
        if animate_transition:
            state_update.update({"active_transition": "PUSH"})

        self.state.update(state_update)

        threading.Thread(target=self._pop_transition).start()

    def render(self, image):
        if len(self.state["stack"]) == 0:
            return image

        x_position = self.state["x_position"]
        foreground_component = self.state["stack"][-1]
        foreground_layer = foreground_component.render(image)

        # if no active transition only the top component needs to be rendered
        if not self.state["active_transition"]:
            return foreground_layer

        # crop foreground so it can be offset to the right by x_position
        crop_boundaries = (0, 0, image.size[0] - x_position, image.size[1])
        cropped_foreground_layer = foreground_layer.crop(crop_boundaries)

        # only foreground exists if one item on the stack
        if len(self.state["stack"]) == 1:
            image.paste(
                cropped_foreground_layer,
                (image.size[0] - cropped_foreground_layer.size[0], 0),
            )
            return image

        # render background layer and paste foreground offset to the right by x_position
        background_component = self.state["stack"][-2]
        background_layer = background_component.render(image)
        background_layer.paste(
            cropped_foreground_layer,
            (image.size[0] - cropped_foreground_layer.size[0], 0),
        )

        return background_layer
