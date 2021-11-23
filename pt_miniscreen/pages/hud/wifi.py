from ipaddress import ip_address

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from ...hotspots.wifi_strength_hotspot import Hotspot as WifiStrengthHotspot
from .network_page_base import NetworkPageData
from .network_page_base import Page as PageBase
from .network_page_base import RowDataGeneric, RowDataText


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            first_row=RowDataGeneric(
                icon_path="sys_info/networking/antenna.png",
                hotspot_type=WifiStrengthHotspot,
            ),
            second_row=RowDataText(
                icon_path="sys_info/networking/wifi.png",
                text=get_wifi_network_ssid,
            ),
            third_row=RowDataText(
                icon_path="sys_info/networking/home.png",
                text=self.get_ip_address,
            ),
        )
        super().__init__(
            size=size, row_data=row_data
        )

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
