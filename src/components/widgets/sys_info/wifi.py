from pitopcommon.sys_info import (
    get_wifi_network_ssid,
    get_internal_ip,
    get_network_strength,
)
from components.widgets.common.functions import get_image_file_path
from components.widgets.common.base_widgets import BaseNetworkingSysInfoSnapshot

from ipaddress import ip_address
from PIL import Image


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "wifi"

        super(Hotspot, self).__init__(
            name=self.name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render
        )

        self.wifi_bars_image = ""

    def reset_extra_data_members(self):
        self.wifi_bars_image = ""

    def is_connected(self):
        return self.second_line != "" and self.third_line != ""

    def set_data_members(self):
        def wifi_strength_image():
            wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100

            if wifi_strength <= 0:
                wifi_signal_strength = "no"
            elif wifi_strength <= 0.25:
                wifi_signal_strength = "weak"
            elif wifi_strength <= 0.5:
                wifi_signal_strength = "okay"
            elif wifi_strength <= 0.75:
                wifi_signal_strength = "good"
            else:
                wifi_signal_strength = "excellent"

            return Image.open(
                get_image_file_path(f"sys_info/networking/wifi_strength_bars/wifi_{wifi_signal_strength}_signal.png")
            )

        self.wifi_bars_image = wifi_strength_image()

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
