import logging
import threading
from math import ceil

from ..hotspot import Hotspot
from ..utils import transition

logger = logging.getLogger(__name__)


class Stack(Hotspot):
    transition_duration = 0.25
    smoothness = 1
    width = 0
    default_state = {
        "x_position": 0,
        "stack": [],
        "active_transition": None,
    }

    def __init__(self, initial_stack=[], **kwargs):
        assert len(initial_stack) > 0
        super().__init__(**kwargs)
        self.state["stack"] = [
            self.create_hotspot(Hotspot) for Hotspot in initial_stack
        ]

    @property
    def active_hotspot(self):
        # when popping the top hotspot is being removed and isn't active
        if self.state["active_transition"] == "POP":
            return self.state["stack"][-2]

        return self.state["stack"][-1]

    @property
    def active_index(self):
        return self.state["stack"].index(self.active_hotspot)

    def _transition(self, on_step):
        for step in transition(
            distance=self.width,
            duration=self.transition_duration,
            base_step=ceil(1 / self.smoothness),
        ):
            on_step(step)

    def _push_transition(self):
        self._transition(
            lambda step: self.state.update(
                {"x_position": self.state["x_position"] - step}
            )
        )

        self.state.update({"active_transition": None})
        logger.debug(f"push final state {self.state}")

    def _pop_transition(self):
        self._transition(
            lambda step: self.state.update(
                {"x_position": self.state["x_position"] + step}
            )
        )

        stack = self.state["stack"]
        self.remove_hotspot(stack.pop())
        self.state.update({"stack": stack, "active_transition": None})
        logger.debug(f"pop final state {self.state}")

    def push(self, Hotspot):
        if self.state["active_transition"] is not None:
            logger.debug(f"Currently transitioning, ignoring push of {Hotspot}")
            return

        logger.debug(f"Starting a new push transition with hotspot {Hotspot}")
        self.state.update(
            {
                "active_transition": "PUSH",
                "x_position": self.width,
                "stack": self.state["stack"] + [self.create_hotspot(Hotspot)],
            }
        )
        logger.debug(f"push initial state {self.state}")

        threading.Thread(target=self._push_transition).start()

    def pop(self):
        if self.state["active_transition"] is not None:
            logger.debug("Currently transitioning, ignoring pop")
            return

        if len(self.state["stack"]) == 1:
            logger.debug("Unable to pop last hotspot from stack, ignoring pop")
            return

        logger.debug("Starting a new pop transition")
        self.state.update(
            {
                "active_transition": "POP",
                "x_position": 0,
            }
        )
        logger.debug(f"push initial state {self.state}")

        threading.Thread(target=self._pop_transition).start()

    def render(self, image):
        x_position = self.state["x_position"]
        foreground_hotspot = self.state["stack"][-1]
        foreground_layer = foreground_hotspot.render(image)

        # if no active transition only the top hotspot needs to be rendered
        if not self.state["active_transition"] or len(self.state["stack"]) < 2:
            return foreground_layer

        # crop foreground so it can be offset to the right by x_position
        crop_boundaries = (0, 0, image.size[0] - x_position, image.size[1])
        cropped_foreground_layer = foreground_layer.crop(crop_boundaries)

        # render background layer and paste foreground offset to the right by x_position
        background_hotspot = self.state["stack"][-2]
        background_layer = background_hotspot.render(image)
        background_layer.paste(
            cropped_foreground_layer,
            (image.size[0] - cropped_foreground_layer.size[0], 0),
        )

        return background_layer
