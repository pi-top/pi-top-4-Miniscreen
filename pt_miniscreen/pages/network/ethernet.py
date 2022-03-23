from functools import partial
from math import ceil

from pitop.common.sys_info import get_internal_ip

from pt_miniscreen.hotspots.table import IconTextRow, Row
from pt_miniscreen.hotspots.table_page import TablePageHotspot
from pt_miniscreen.utils import get_image_file_path


class EthernetPage(TablePageHotspot):
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
                    text_align_rounding_fn=ceil,
                ),
                Row,  # empty row
            ]
        )
