from ipaddress import ip_address

from PIL import Image
from pitop.common.sys_info import (
    get_internal_ip,
    get_network_strength,
    get_wifi_network_ssid,
)

from ...utils import get_image_file_path
from ..widgets.common import BaseNetworkingSysInfoSnapshot

wifi_images = {
    "no": Image.open(
        get_image_file_path("sys_info/networking/wifi_strength_bars/wifi_no_signal.png")
    ),
    "weak": Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_weak_signal.png"
        )
    ),
    "okay": Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_okay_signal.png"
        )
    ),
    "good": Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_good_signal.png"
        )
    ),
    "excellent": Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_excellent_signal.png"
        )
    ),
}


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "wifi"
        self.human_readable_name = "WiFi"

        super(Hotspot, self).__init__(
            name=self.name,
            human_readable_name=self.human_readable_name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render,
        )

        self.wifi_bars_image = ""

    def reset_extra_data_members(self):
        self.wifi_bars_image = ""

    def is_connected(self):
        return self.second_line != "" and self.third_line != ""

    def set_data_members(self):
        wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100

        if wifi_strength <= 0:
            self.wifi_bars_image = wifi_images["no"]
        elif wifi_strength <= 0.25:
            self.wifi_bars_image = wifi_images["weak"]
        elif wifi_strength <= 0.5:
            self.wifi_bars_image = wifi_images["okay"]
        elif wifi_strength <= 0.75:
            self.wifi_bars_image = wifi_images["good"]
        else:
            self.wifi_bars_image = wifi_images["excellent"]

        network_ssid = get_wifi_network_ssid()
        if network_ssid != "Error":
            self.second_line = network_ssid

        network_ip = get_internal_ip(iface="wlan0")
        try:
            self.third_line = ip_address(network_ip)
        except ValueError:
            self.third_line = ""

    def render_extra_info(self, draw):
        draw.bitmap(
            xy=(5, 0),
            bitmap=self.wifi_bars_image,
            fill="white",
        )
