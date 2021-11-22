from ipaddress import ip_address
from typing import Dict

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from pt_miniscreen.state import Speeds

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.wifi_strength_hotspot import Hotspot as WifiStrengthHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


class Page(PageBase):
    def __init__(self, size, mode, config):
        super().__init__(size=size, mode=mode, config=config)
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
        COMMON_THIRD_LINE_Y = COMMON_SECOND_LINE_Y + DELTA_Y
        ICON_X_POS = 10
        DEFAULT_FONT_SIZE = 12

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=self.size,
                    image_path=get_image_file_path("sys_info/networking/antenna.png"),
                    xy=(ICON_X_POS, COMMON_FIRST_LINE_Y),
                ),
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=self.size,
                    image_path=get_image_file_path("sys_info/networking/wifi.png"),
                    xy=(ICON_X_POS, COMMON_SECOND_LINE_Y),
                ),
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=self.size,
                    image_path=get_image_file_path("sys_info/networking/home.png"),
                    xy=(ICON_X_POS, COMMON_THIRD_LINE_Y),
                ),
            ],
            (MARGIN_X_LEFT, COMMON_FIRST_LINE_Y - 1): [
                WifiStrengthHotspot(
                    interval=self.interval,
                    size=(self.width - MARGIN_X_LEFT - MARGIN_X_RIGHT, ICON_HEIGHT),
                    mode=self.mode,
                )
            ],
            (MARGIN_X_LEFT, COMMON_SECOND_LINE_Y - 1): [
                MarqueeTextHotspot(
                    interval=Speeds.MARQUEE.value,
                    mode=self.mode,
                    size=(self.width - MARGIN_X_LEFT - MARGIN_X_RIGHT, ROW_HEIGHT),
                    text=get_wifi_network_ssid,
                    font_size=DEFAULT_FONT_SIZE,
                ),
            ],
            (MARGIN_X_LEFT, COMMON_THIRD_LINE_Y - 1): [
                MarqueeTextHotspot(
                    interval=Speeds.MARQUEE.value,
                    mode=self.mode,
                    size=(self.width - MARGIN_X_LEFT - MARGIN_X_RIGHT, ROW_HEIGHT),
                    text=self.get_ip_address,
                    font_size=DEFAULT_FONT_SIZE,
                ),
            ],
        }

    def get_ip_address(self):
        ip = ""
        try:
            network_ip_candidate = get_internal_ip(iface="wlan0")
            ip_address(network_ip_candidate)
            ip = network_ip_candidate
        except ValueError:
            pass
        finally:
            return ip
