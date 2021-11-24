from ...hotspots.base import HotspotInstance
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

        self.hotspot_instances = [
            HotspotInstance(
                ImageHotspot(
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
                (0, self.offset_pos_for_vertical_center(ICON_SIZE)),
            ),
            HotspotInstance(
                CpuBarsHotspot(
                    size=(
                        self.long_section_width,
                        cpu_bar_hotspot_height,
                    ),
                ),
                (
                    self.short_section_width,
                    self.offset_pos_for_vertical_center(cpu_bar_hotspot_height),
                ),
            ),
        ]
