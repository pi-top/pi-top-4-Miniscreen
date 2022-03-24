from functools import partial

from pitop.common.sys_info import get_internal_ip

from pt_miniscreen.components.icon_text_row import IconTextRow, Row
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.utils import get_image_file_path


class EthernetPage(InfoPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Ethernet",
            Rows=[
                Row,  # empty row
                partial(
                    IconTextRow,
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                    get_text=lambda: get_internal_ip(iface="eth0"),
                ),
                Row,  # empty row
            ]
        )
