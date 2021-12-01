from typing import List, Tuple

from ..hotspots.base import HotspotInstance
from ..types import Coordinate


class Page:
    def __init__(self, size: Coordinate, child_menu_cls=None) -> None:
        self._size = size
        self.child_menu_cls = child_menu_cls

        self.invert = False
        self.visible = True
        self.font_size = 14
        self.wrap = True

        golden_ratio = (1 + 5 ** 0.5) / 2
        self.long_section_width = int(self.width / golden_ratio)
        self.short_section_width = self.width - self.long_section_width

        self.hotspot_instances: List[HotspotInstance] = list()

    @property
    def size(self) -> Tuple:
        return self._size

    @size.setter
    def size(self, value: Coordinate):
        self._size = value
        # Resize hotspots
        self.reset()

    def reset(self) -> None:
        pass

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

    def on_select_press(self):
        # Only invoked if there is no child menu in config
        pass

    def offset_pos_for_vertical_center(self, hotspot_height: int) -> int:
        return int((self.height - hotspot_height) / 2)
