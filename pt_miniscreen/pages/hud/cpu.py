from typing import Dict

from ...hotspots.cpu_bars_hotspot import Hotspot as CpuBarsHotspot
from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)

    def reset(self):
        cpu_bars_y_margin = self.height * 0.3
        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    size=(self.short_section_width, self.height),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
            ],
            (self.short_section_width, int(cpu_bars_y_margin / 2)): [
                CpuBarsHotspot(
                    size=(
                        self.long_section_width,
                        int(self.height - cpu_bars_y_margin),
                    ),
                ),
            ],
        }
