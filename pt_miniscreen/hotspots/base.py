from dataclasses import dataclass
from time import perf_counter
from typing import Tuple

from PIL import Image, ImageOps
from pitop.miniscreen.oled.assistant import MiniscreenAssistant


class Hotspot:
    def __init__(self, interval, size):
        self.interval = interval
        self.size = size

        self.draw_white = True
        self.draw_black = False

        self.last_updated = -self.interval
        self.invert = False
        self.width = size[0]
        self.height = size[1]

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, value):
        self.size = (value, self.height)

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, value):
        self.size = (self.width, value)

    def should_redraw(self):
        if not self.draw_white and not self.draw_black:
            return False

        """Only requests a redraw after ``interval`` seconds have elapsed."""
        return perf_counter() - self.last_updated > self.interval

    @property
    def image(self):
        hotspot_image = Image.new("1", self.size)
        self.render(hotspot_image)
        self.last_updated = perf_counter()
        return hotspot_image

    def render(self, image):
        raise NotImplementedError

    def paste_into(self, image, xy):
        if not self.draw_white and not self.draw_black:
            return

        hotspot_image = Image.new("1", self.size)
        self.render(hotspot_image)

        if self.invert:
            hotspot_image = MiniscreenAssistant("1", self.size).invert(hotspot_image)

        mask = None
        if self.draw_white and not self.draw_black:
            mask = hotspot_image

        elif not self.draw_white and self.draw_black:
            mask = ImageOps.invert(hotspot_image)

        image.paste(hotspot_image, xy, mask)

    def mask(self, hotspot_image):
        mask = None
        if self.draw_white and not self.draw_black:
            mask = hotspot_image

        elif not self.draw_white and self.draw_black:
            mask = ImageOps.invert(hotspot_image)

        elif self.draw_white and self.draw_black:
            mask = Image.new("1", size=hotspot_image.size, fill="white")
        return mask


@dataclass
class HotspotInstance:
    hotspot: Hotspot
    xy: Tuple[int, int]
