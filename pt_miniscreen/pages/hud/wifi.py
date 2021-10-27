from ipaddress import ip_address
from typing import Dict

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...hotspots.wifi_strength_hotspot import Hotspot as WifiStrengthHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

default_margin_x = 29

common_first_line_y = 16
common_second_line_y = common_first_line_y + 16
common_third_line_y = common_second_line_y + 16


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        icon_height = 12

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path(
                        "sys_info/networking/wifi_strength_bar.png"
                    ),
                    xy=(default_margin_x / 3, common_first_line_y - icon_height / 2),
                ),
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_ssid.png"),
                    xy=(default_margin_x / 3, common_second_line_y - icon_height / 2),
                ),
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_ip.png"),
                    xy=(default_margin_x / 3, common_third_line_y - icon_height / 2),
                ),
                TextHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    text=get_wifi_network_ssid,
                    font_size=12,
                    xy=(default_margin_x, common_second_line_y),
                    anchor="lm",
                    align="left",
                ),
                TextHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    text=self.get_ip_address,
                    font_size=12,
                    xy=(default_margin_x, common_third_line_y),
                    anchor="lm",
                    align="left",
                ),
            ],
            (default_margin_x, int(common_first_line_y - icon_height / 2)): [
                WifiStrengthHotspot(
                    interval=interval,
                    size=(int(size[0] / 3), 12),
                    mode=mode,
                )
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
