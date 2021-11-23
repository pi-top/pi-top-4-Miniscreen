from typing import Dict

from pitop.common.sys_info import get_internal_ip

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


class Page(PageBase):
    def __init__(self, size, mode):
        super().__init__(size=size, mode=mode)
        self.setup_hotspots()

    def setup_hotspots(self):
        MARGIN_X_LEFT = 30
        MARGIN_X_RIGHT = 10
        SCALE = self.height / 64.0
        ICON_HEIGHT = 12
        VERTICAL_SPACING = 4
        ROW_HEIGHT = ICON_HEIGHT + VERTICAL_SPACING
        DELTA_Y = int(ROW_HEIGHT * SCALE)
        COMMON_FIRST_LINE_Y = int(10 * SCALE)
        COMMON_SECOND_LINE_Y = COMMON_FIRST_LINE_Y + DELTA_Y
        ICON_X_POS = 10
        DEFAULT_FONT_SIZE = 12

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=1,
                    mode=self.mode,
                    size=self.size,
                    image_path=get_image_file_path("sys_info/networking/home.png"),
                    xy=(ICON_X_POS, COMMON_SECOND_LINE_Y),
                ),
            ],
            (MARGIN_X_LEFT, COMMON_SECOND_LINE_Y - 1): [
                MarqueeTextHotspot(
                    mode=self.mode,
                    size=(self.width - MARGIN_X_LEFT - MARGIN_X_RIGHT, ROW_HEIGHT),
                    text=lambda: get_internal_ip(iface="wlan0"),
                    font_size=DEFAULT_FONT_SIZE,
                ),
            ],
        }
