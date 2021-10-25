from typing import Dict

from ...hotspots.cpu_bars_hotspot import Hotspot as CpuBarsHotspot
from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...utils import get_image_file_path
from ..base import PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)

        golden_ratio = (1 + 5 ** 0.5) / 2
        long_section_width = int(size[0] / golden_ratio)

        y_margin = 20
        cpu_bars_hotspot_pos = (long_section_width, int(y_margin / 2))
        cpu_bars_hotspot_size = (
            size[0] - cpu_bars_hotspot_pos[0],
            size[1] - y_margin,
        )

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=(long_section_width, size[1]),
                    image_path=get_image_file_path("sys_info/cpu.png"),
                ),
            ],
            cpu_bars_hotspot_pos: [
                CpuBarsHotspot(
                    interval=interval, mode=mode, size=cpu_bars_hotspot_size
                ),
            ],
        }
