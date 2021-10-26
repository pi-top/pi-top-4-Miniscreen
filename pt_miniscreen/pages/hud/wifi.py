from ipaddress import ip_address
from typing import Dict

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...hotspots.wifi_strength_hotspot import Hotspot as WifiStrengthHotspot
from ...utils import get_image_file_path
from ..base import PageBase
from .base import common_second_line_y, common_third_line_y, default_margin_x


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.ssid = ""
        self.ip = ""

        self.ssid_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=size,
            text=get_wifi_network_ssid,
            font_size=12,
            xy=(default_margin_x, common_second_line_y),
        )
        self.ip_address_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=size,
            text=self.get_ip_address,
            font_size=12,
            xy=(default_margin_x, common_third_line_y),
        )
        self.wifi_strength = WifiStrengthHotspot(
            interval=interval, size=size, mode=mode, image_path=None, xy=(0, 0)
        )

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_info.png"),
                ),
                self.ssid_hotspot,
                self.ip_address_hotspot,
                self.wifi_strength,
            ]
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
