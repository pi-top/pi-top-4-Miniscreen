import datetime
import math

from PIL import ImageDraw

from ..types import Coordinate
from .base import Hotspot as HotspotBase


def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)


class Hotspot(HotspotBase):
    def __init__(self, size: Coordinate):
        super().__init__(interval=1, size=size)

    def render(self, image):
        draw = ImageDraw.Draw(image)

        now = datetime.datetime.now()

        y_offset = 16
        margin = 3

        cx = self.width / 2
        cy = y_offset + ((self.height - y_offset - margin) / 2)

        left = (self.width - (min(self.height, 64) - y_offset - margin)) / 2
        right = self.width - left
        radius = (right - left) / 2
        top = cy - radius
        bottom = cy + radius

        hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
        hrs = posn(hrs_angle, radius - 8)

        min_angle = 270 + (6 * now.minute)
        mins = posn(min_angle, radius - 3)

        sec_angle = 270 + (6 * now.second)
        secs = posn(sec_angle, radius - 3)

        draw.ellipse((left, top, right, bottom), outline="white")
        draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
        draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
        draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
        draw.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill="white", outline="white")
