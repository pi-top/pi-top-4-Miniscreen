import logging
from math import floor

import PIL.Image

from ..pages.settings_connection.action_state import ActionState
from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval, size, mode)
        self.processing_frame_no = 0
        self.circle_size = max(2, floor(size[0] / 8))
        self._action_state = ActionState.UNKNOWN

    @property
    def action_state(self):
        return self._action_state

    @action_state.setter
    def action_state(self, state):
        if self.action_state != ActionState.PROCESSING:
            self.processing_frame_no = 0

        self._action_state = state

    def render(self, image):
        PIL.ImageDraw.Draw(image).ellipse(
            xy=[(0, 0), self.size],
            fill="white",
        )

        if self.action_state == ActionState.UNKNOWN:
            # TODO: question mark
            pass

        elif self.action_state == ActionState.ENABLED:
            # TODO: check mark
            pass

        elif self.action_state == ActionState.DISABLED:
            # TODO: cross
            pass

        elif self.action_state == ActionState.PROCESSING:
            center = (self.size[0] / 2, self.size[1] / 2)
            off_left = (center[0] / 2, center[1])
            off_right = (center[0] * 3 / 2, center[1])

            for index, dot in enumerate([off_left, center, off_right]):
                if index > self.processing_frame_no:
                    break

                PIL.ImageDraw.Draw(image).ellipse(
                    xy=[
                        (
                            int(dot[0] - floor(self.circle_size / 2)),
                            int(dot[1] - floor(self.circle_size / 2)),
                        ),
                        (
                            int(dot[0] + floor(self.circle_size / 2)),
                            int(dot[1] + floor(self.circle_size / 2)),
                        ),
                    ],
                    fill="black",
                )

            self.processing_frame_no = (self.processing_frame_no + 1) % 3
