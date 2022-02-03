from pitop.common.sys_info import get_ap_mode_status

from .network_page_base import NetworkPageData
from .network_page_base import Page as PageBase
from .network_page_base import RowDataText


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            first_row=RowDataText(
                icon_path="sys_info/networking/antenna.png",
                text=lambda: get_ap_mode_status().get("ssid", ""),
            ),
            second_row=RowDataText(
                icon_path="sys_info/networking/padlock.png",
                text=lambda: get_ap_mode_status().get("passphrase", ""),
            ),
            third_row=RowDataText(
                icon_path="sys_info/networking/home.png",
                text=lambda: get_ap_mode_status().get("ip_address", ""),
            ),
        )
        super().__init__(size=size, row_data=row_data)
