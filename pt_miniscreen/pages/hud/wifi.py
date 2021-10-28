from ipaddress import ip_address
from typing import Dict

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.wifi_strength_hotspot import Hotspot as WifiStrengthHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

MARGIN_X_LEFT = 29
MARGIN_X_RIGHT = 10
COMMON_FIRST_LINE_Y = 16
COMMON_SECOND_LINE_Y = COMMON_FIRST_LINE_Y + 16
COMMON_THIRD_LINE_Y = COMMON_SECOND_LINE_Y + 16
ICON_HEIGHT = 12


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path(
                        "sys_info/networking/wifi_strength_bar.png"
                    ),
                    xy=(MARGIN_X_LEFT / 3, int(COMMON_FIRST_LINE_Y - ICON_HEIGHT / 2)),
                ),
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_ssid.png"),
                    xy=(MARGIN_X_LEFT / 3, int(COMMON_SECOND_LINE_Y - ICON_HEIGHT / 2)),
                ),
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_ip.png"),
                    xy=(MARGIN_X_LEFT / 3, int(COMMON_THIRD_LINE_Y - ICON_HEIGHT / 2)),
                ),
            ],
            (MARGIN_X_LEFT, int(COMMON_FIRST_LINE_Y - ICON_HEIGHT / 2)): [
                WifiStrengthHotspot(
                    interval=interval,
                    size=(size[0] - MARGIN_X_LEFT - MARGIN_X_RIGHT, ICON_HEIGHT),
                    mode=mode,
                )
            ],
            (MARGIN_X_LEFT, int(COMMON_SECOND_LINE_Y - ICON_HEIGHT / 2)): [
                MarqueeTextHotspot(
                    interval=interval,
                    mode=mode,
                    size=(size[0] - MARGIN_X_LEFT - MARGIN_X_RIGHT, ICON_HEIGHT),
                    text=get_wifi_network_ssid,
                    font_size=12,
                ),
            ],
            (MARGIN_X_LEFT, int(COMMON_THIRD_LINE_Y - ICON_HEIGHT / 2)): [
                MarqueeTextHotspot(
                    interval=interval,
                    mode=mode,
                    size=(size[0] - MARGIN_X_LEFT - MARGIN_X_RIGHT, ICON_HEIGHT),
                    text=self.get_ip_address,
                    font_size=12,
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
