from ...hotspots.base import HotspotInstance
from ...hotspots.cpu_bars import Hotspot as CpuBarsHotspot
from ...hotspots.templates.image import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

ICON_SIZE = 38
ICON_LEFT_MARGIN = 8
CPU_BARS_LEFT_MARGIN = 5
CPU_BARS_TOTAL_WIDTH = 50


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)
        self.reset()

    def reset(self):
        cpu_bar_hotspot_height = int(self.height * 0.7)

        self.hotspot_instances = [
            HotspotInstance(
                ImageHotspot(
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
                (ICON_LEFT_MARGIN, self.offset_pos_for_vertical_center(ICON_SIZE)),
            ),
            HotspotInstance(
                CpuBarsHotspot(
                    size=(
                        CPU_BARS_TOTAL_WIDTH,
                        cpu_bar_hotspot_height,
                    ),
                ),
                (
                    CPU_BARS_LEFT_MARGIN + ICON_SIZE + ICON_LEFT_MARGIN,
                    self.offset_pos_for_vertical_center(cpu_bar_hotspot_height),
                ),
            ),
        ]
