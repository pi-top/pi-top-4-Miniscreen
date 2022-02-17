from pitop.common.sys_info import get_ap_mode_status

from .network_page_base import NetworkPageData
from .network_page_base import Page as PageBase
from .network_page_base import RowDataText


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            first_row=RowDataText(
                icon_path="sys_info/networking/wifi-small.png",
                text=lambda: get_ap_mode_status().get("ssid", "Not active"),
            ),
            second_row=RowDataText(
                icon_path="sys_info/networking/padlock-small.png",
                text=lambda: get_ap_mode_status().get("passphrase", ""),
            ),
            third_row=RowDataText(
                icon_path="sys_info/networking/home-small.png",
                text=lambda: get_ap_mode_status().get("ip_address", ""),
            ),
        )
        super().__init__(size=size, row_data=row_data, title="Wi-Fi Hotspot")
