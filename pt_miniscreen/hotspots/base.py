from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageOps
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..types import CachedImage, Coordinate


class Hotspot:
    def __init__(self, interval: float, size: Coordinate):
        self._interval: float = interval
        self.size: Coordinate = size

        self.draw_white: bool = True
        self.draw_black: bool = False

        self.invert: bool = False
        self.width: int = size[0]
        self.height: int = size[1]

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, interval: float) -> None:
        self._interval = interval

    @property
    def width(self) -> int:
        return self.size[0]

    @width.setter
    def width(self, value: int) -> None:
        self.size = (value, self.height)

    @property
    def height(self) -> int:
        return self.size[1]

    @height.setter
    def height(self, value: int) -> None:
        self.size = (self.width, value)

    @property
    def image(self) -> Image.Image:
        hotspot_image = Image.new("1", self.size)

        if not self.draw_white and not self.draw_black:
            return hotspot_image

        self.render(hotspot_image)

        if self.invert:
            hotspot_image = MiniscreenAssistant("1", self.size).invert(hotspot_image)

        self.render(hotspot_image)
        return hotspot_image

    def render(self, image: Image.Image) -> None:
        raise NotImplementedError

    def create_mask(self, image: Optional[Image.Image] = None) -> Image.Image:
        if image is None:
            image = self.image

        # 'superimpose'
        white_only = self.draw_white and not self.draw_black

        # 'paste over'
        white_and_black = self.draw_black and not self.draw_white

        # 'inverted superimpose'
        black_only = self.draw_black and not self.draw_white

        if white_only:
            mask = image

        elif black_only:
            mask = ImageOps.invert(image)

        elif white_and_black:
            mask = Image.new("1", size=image.size, color="white")

        else:  # nothing (no effect) = not self.draw_black and not self.draw_black
            mask = Image.new("1", size=image.size, color="black")

        return mask

    def get_new_image(self) -> CachedImage:
        image = self.image
        return (image, self.create_mask(image))


@dataclass
class HotspotInstance:
    hotspot: Hotspot
    xy: Coordinate

    @property
    def size(self) -> Coordinate:
        return self.hotspot.size
