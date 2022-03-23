from functools import partial
from math import ceil

from pitop.common.sys_info import get_ap_mode_status

from pt_miniscreen.hotspots.table import IconTextRow
from pt_miniscreen.hotspots.table_page import TablePageHotspot
from pt_miniscreen.utils import get_image_file_path


class APPage(TablePageHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Wi-Fi Hotspot",
            Rows=[
                partial(
                    IconTextRow,
                    icon_path=get_image_file_path("sys_info/networking/wifi-small.png"),
                    get_text=lambda: get_ap_mode_status().get("ssid", "Not active"),
                    text_align_rounding_fn=ceil,
                ),
                partial(
                    IconTextRow,
                    icon_path=get_image_file_path(
                        "sys_info/networking/padlock-small.png"
                    ),
                    get_text=lambda: get_ap_mode_status().get("passphrase", ""),
                    text_align_rounding_fn=ceil,
                ),
                partial(
                    IconTextRow,
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                    get_text=lambda: get_ap_mode_status().get("ip_address", ""),
                    text_align_rounding_fn=ceil,
                ),
            ]
        )
