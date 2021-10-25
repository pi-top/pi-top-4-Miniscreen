import PIL.Image

from .base import HotspotBase


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode, bounding_box=None):
        super().__init__(interval, size, mode)

        if bounding_box is None:
            bounding_box = (0, 0) + self.size
        self.bounding_box = bounding_box

    def render(self, image):
        if image:
            PIL.ImageDraw.Draw(image).rectangle(self.bounding_box, "white", "white")
