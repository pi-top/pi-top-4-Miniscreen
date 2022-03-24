from functools import partial
from ipaddress import ip_address

from pitop.common.sys_info import get_internal_ip

from pt_miniscreen.components.icon_text_row import IconTextRow, Row
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.utils import get_image_file_path


def get_ip_address():
    ip_addr = ""
    try:
        candidate = get_internal_ip(iface="ptusb0")
        ip_address(candidate)
        ip_addr = candidate
    except ValueError:
        pass
    return ip_addr


class USBPage(InfoPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="USB",
            Rows=[
                Row,  # empty row
                partial(
                    IconTextRow,
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                    get_text=get_ip_address,
                ),
                Row,  # empty row
            ]
        )
