from functools import partial
from ipaddress import ip_address
from math import ceil

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from pt_miniscreen.hotspots.image import ImageHotspot
from pt_miniscreen.hotspots.table import IconTextRow, Row
from pt_miniscreen.hotspots.table_page import TablePageHotspot
from pt_miniscreen.hotspots.wifi_strength import WifiStrengthHotspot
from pt_miniscreen.utils import get_image_file_path


def get_ssid():
    ssid = get_wifi_network_ssid()
    if ssid == "Error":
        return "Not connected"

    return ssid


def get_ip_address():
    ip = ""
    try:
        network_ip_candidate = get_internal_ip(iface="wlan0")
        ip_address(network_ip_candidate)
        ip = network_ip_candidate
    except ValueError:
        pass
    finally:
        return ip


class WifiPage(TablePageHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Wi-Fi",
            Rows=[
                partial(
                    Row,
                    column_widths=[15, "auto"],
                    Columns=[
                        partial(
                            ImageHotspot,
                            vertical_align="center",
                            image_path=get_image_file_path(
                                "sys_info/networking/antenna-small.png"
                            ),
                        ),
                        WifiStrengthHotspot,
                    ],
                ),
                partial(
                    IconTextRow,
                    get_text=get_ssid,
                    icon_path=get_image_file_path("sys_info/networking/wifi-small.png"),
                    text_align_rounding_fn=ceil,
                ),
                partial(
                    IconTextRow,
                    get_text=get_ip_address,
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                    text_align_rounding_fn=ceil,
                ),
            ]
        )
