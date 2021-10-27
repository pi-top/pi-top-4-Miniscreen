import logging
from math import floor

import PIL.Image

from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval, size, mode)
        self.frame_no = 0
        self.circle_size = max(2, floor(size[0] / 8))

    def render(self, image):
        PIL.ImageDraw.Draw(image).ellipse(
            xy=[(0, 0), self.size],
            fill="white",
        )

        center = (self.size[0] / 2, self.size[1] / 2)
        off_left = (center[0] / 2, center[1])
        off_right = (center[0] * 3 / 2, center[1])

        for index, dot in enumerate([off_left, center, off_right]):
            if index > self.frame_no:
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

        self.frame_no = (self.frame_no + 1) % 3
