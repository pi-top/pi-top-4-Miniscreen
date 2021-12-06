import logging
from dataclasses import dataclass

from PIL import Image

from ...types import Coordinate
from .hotspot import Hotspot

logger = logging.getLogger(__name__)


@dataclass
class HotspotInstance:
    hotspot: Hotspot
    xy: Coordinate

    @property
    def size(self) -> Coordinate:
        return self.hotspot.size

    def start(self) -> None:
        self.hotspot.start()

    @property
    def active(self) -> bool:
        return self.hotspot.active

    @active.setter
    def active(self, is_active: bool) -> None:
        self.hotspot.active = is_active

    def paste_into_image(self, image: Image.Image) -> None:
        will_paste = self.hotspot.draw_white or self.hotspot.draw_black
        if not will_paste:
            return

        image.paste(
            self.hotspot.image, self.xy, self.hotspot.get_mask(self.hotspot.image)
        )

    def is_visible_in_window(
        self, window_position: Coordinate, window_size: Coordinate
    ) -> bool:
        def calc_bounds(xy, size):
            """For width and height attributes, determine the bounding box if
            were positioned at ``(x, y)``."""
            left, top = xy
            width, height = size
            right = left + width
            bottom = top + height
            return [left, top, right, bottom]

        def range_overlap(a_min, a_max, b_min, b_max):
            """Neither range is completely greater than the other."""
            return (a_min < b_max) and (b_min < a_max)

        l1, t1, r1, b1 = calc_bounds(self.xy, self.size)
        l2, t2, r2, b2 = calc_bounds(window_position, window_size)
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    def paste_into_image_if_visible_in_window(
        self, image: Image.Image, window_position: Coordinate, window_size: Coordinate
    ):
        if self.is_visible_in_window(window_position, window_size):
            self.paste_into_image(image)

    def set_active_based_on_if_visible_in_window(
        self, window_position: Coordinate, window_size: Coordinate
    ):
        self.active = self.is_visible_in_window(window_position, window_size)
