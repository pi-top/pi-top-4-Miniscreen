import PIL.Image

from ...state import Speeds
from ..base import Hotspot as HotspotBase


class Hotspot(HotspotBase):
    def __init__(
        self, size, bounding_box=None, interval=Speeds.DYNAMIC_PAGE_REDRAW.value
    ):
        super().__init__(interval=interval, size=size)

        if bounding_box is None:
            bounding_box = (0, 0) + self.size
        self.bounding_box = bounding_box

    def render(self, image):
        if (
            self.bounding_box[0] == self.bounding_box[2]
            or self.bounding_box[1] == self.bounding_box[3]
        ):
            return
        if image:
            PIL.ImageDraw.Draw(image).rectangle(self.bounding_box, "white", "white")
