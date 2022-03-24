from functools import partial
from ipaddress import ip_address

from pitop.common.sys_info import get_internal_ip, get_wifi_network_ssid

from pt_miniscreen.components.icon_text_row import IconTextRow, Row
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.components.wifi_strength import WifiStrength
from pt_miniscreen.core.components.image import Image
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


class WifiPage(InfoPage):
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
                            Image,
                            vertical_align="center",
                            image_path=get_image_file_path(
                                "sys_info/networking/antenna-small.png"
                            ),
                        ),
                        WifiStrength,
                    ],
                ),
                partial(
                    IconTextRow,
                    get_text=get_ssid,
                    icon_path=get_image_file_path("sys_info/networking/wifi-small.png"),
                ),
                partial(
                    IconTextRow,
                    get_text=get_ip_address,
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                ),
            ]
        )
