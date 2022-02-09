import PIL.ImageDraw

from .base import Hotspot as HotspotBase


class Hotspot(HotspotBase):
    def __init__(
        self,
        interval,
        size,
        bar_height,
        bar_y_start=0,
        bar_padding=3,
    ):
        super().__init__(interval=interval, size=size)
        self.bar_height = bar_height
        self.bar_padding = bar_padding
        self.bar_y_pos = bar_y_start

    def render(self, image):
        PIL.ImageDraw.Draw(image).rectangle(
            (
                self.bar_padding,
                self.bar_y_pos + self.bar_padding,
                self.size[0] - self.bar_padding,
                self.bar_y_pos + self.bar_height - self.bar_padding,
            ),
            fill="white",
        )
