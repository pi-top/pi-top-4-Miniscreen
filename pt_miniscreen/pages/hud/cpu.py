from typing import Dict

from ...hotspots.cpu_bars_hotspot import Hotspot as CpuBarsHotspot
from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        cpu_bars_y_margin = 20
        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=(self.short_section_width, size[1]),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
            ],
            (self.short_section_width, int(cpu_bars_y_margin / 2)): [
                CpuBarsHotspot(
                    interval=interval,
                    mode=mode,
                    size=(self.long_section_width, size[1] - cpu_bars_y_margin),
                ),
            ],
        }
