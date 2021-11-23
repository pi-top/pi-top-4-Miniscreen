from typing import Dict

from ...hotspots.cpu_bars_hotspot import Hotspot as CpuBarsHotspot
from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

ICON_SIZE = 38


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)

    def reset(self):
        cpu_bar_hotspot_height = int(self.height * 0.7)

        self.hotspots: Dict = {
            (0, self.offset_pos_for_vertical_center(ICON_SIZE)): [
                ImageHotspot(
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
            ],
            (
                self.short_section_width,
                self.offset_pos_for_vertical_center(cpu_bar_hotspot_height),
            ): [
                CpuBarsHotspot(
                    size=(
                        self.long_section_width,
                        cpu_bar_hotspot_height,
                    ),
                ),
            ],
        }
