from typing import Dict

from ...hotspots.cpu_bars_hotspot import Hotspot as CpuBarsHotspot
from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

ICON_SIZE = 38


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.setup_hotspots()

    def setup_hotspots(self):
        cpu_bar_hotspot_height = int(self.height * 0.7)

        self.hotspots: Dict = {
            (0, self.vertical_middle_position(ICON_SIZE)): [
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
            ],
            (
                self.short_section_width,
                self.vertical_middle_position(cpu_bar_hotspot_height),
            ): [
                CpuBarsHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=(
                        self.long_section_width,
                        cpu_bar_hotspot_height,
                    ),
                ),
            ],
        }
