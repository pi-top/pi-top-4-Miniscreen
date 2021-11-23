from pitop.common.sys_info import get_internal_ip

from .network_page_base import NetworkPageData
from .network_page_base import Page as PageBase
from .network_page_base import RowDataText


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        row_data = NetworkPageData(
            second_row=RowDataText(
                icon_path="sys_info/networking/home.png",
                text=lambda: get_internal_ip(iface="eth0"),
            ),
        )
        super().__init__(
            interval=interval, size=size, mode=mode, config=config, row_data=row_data
        )
