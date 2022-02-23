from getpass import getuser
from ipaddress import ip_address

from pitop.common.pt_os import is_pi_using_default_password
from pitop.common.sys_info import get_internal_ip

from .network_page_base import NetworkPageData
from .network_page_base import Page as PageBase
from .network_page_base import RowDataText


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            second_row=RowDataText(
                icon_path="sys_info/networking/home-small.png",
                text=self.get_ip_address,
            ),
        )
        super().__init__(size=size, row_data=row_data, title="USB")

    def get_user(self):
        return "pi" if getuser() == "root" else getuser()

    def get_password(self):
        return "pi-top" if is_pi_using_default_password() is True else "********"

    def get_ip_address(self):
        ip_addr = ""
        try:
            candidate = get_internal_ip(iface="ptusb0")
            ip_address(candidate)
            ip_addr = candidate
        except ValueError:
            pass
        return ip_addr
