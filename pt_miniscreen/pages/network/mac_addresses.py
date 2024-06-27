from functools import partial

import psutil

from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText


iface_name_lookup = {
    "eth0": "Eth",
    "wlan0": "WiFi",
    "wlan_ap0": "AP",
}


def iface_mac_address(iface_name: str) -> str:
    txt = ""

    try:
        nics = psutil.net_if_addrs()
    except Exception:
        return txt

    if iface_name in nics:
        for data in nics[iface_name]:
            if (
                hasattr(data, "family")
                and hasattr(data, "address")
                and data.family == psutil.AF_LINK
            ):
                txt = f"{iface_name_lookup.get(iface_name)}: {data.address}"
                break

    return txt


class MacAddressesPage(InfoPage):
    def __init__(self, **kwargs):
        Row = partial(MarqueeText, font_size=10, vertical_align="center")

        super().__init__(
            **kwargs,
            title="MAC addresses",
            Rows=[
                partial(Row, text=iface_mac_address("wlan0")),
                partial(Row, text=iface_mac_address("eth0")),
                partial(Row, text=iface_mac_address("wlan_ap0")),
            ],
        )
