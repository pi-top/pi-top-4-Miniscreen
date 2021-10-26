from ipaddress import ip_address
from typing import Dict

import PIL.Image
import PIL.ImageDraw
from pitop.common.sys_info import (
    get_internal_ip,
    get_network_strength,
    get_wifi_network_ssid,
)

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import PageBase
from .base import common_second_line_y, common_third_line_y, default_margin_x

wifi_images = {
    "no": PIL.Image.open(
        get_image_file_path("sys_info/networking/wifi_strength_bars/wifi_no_signal.png")
    ),
    "weak": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_weak_signal.png"
        )
    ),
    "okay": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_okay_signal.png"
        )
    ),
    "good": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_good_signal.png"
        )
    ),
    "excellent": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_excellent_signal.png"
        )
    ),
}


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)

        self.ssid_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=size,
            text="ssid",
            font_size=12,
            xy=(default_margin_x, common_second_line_y),
        )
        self.ip_address_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=size,
            text="pi-top.local",
            font_size=12,
            xy=(default_margin_x, common_third_line_y),
        )

        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    image_path=get_image_file_path("sys_info/networking/wifi_info.png"),
                ),
                self.ssid_hotspot,
                self.ip_address_hotspot,
            ]
        }

        self.wifi_bars_image = wifi_images["no"]
        self.info_image = PIL.Image.open(
            get_image_file_path("sys_info/networking/wifi_info.png")
        )

    def draw_wifi_strength(self, image):
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

        PIL.ImageDraw.Draw(image).bitmap(
            xy=(0, 0),
            bitmap=self.wifi_bars_image.convert(self.mode),
            fill="white",
        )

    def draw_info_image(self, image):
        draw = PIL.ImageDraw.Draw(image)

        draw.bitmap(
            xy=(0, 0),
            bitmap=self.info_image,
            fill="white",
        )

    def draw_info_text(self, image):
        self.ssid_hotspot.text = get_wifi_network_ssid()

        network_ip = ""
        try:
            network_ip_candidate = get_internal_ip(iface="wlan0")
            ip_address(network_ip_candidate)
            network_ip = network_ip_candidate

        except ValueError:
            pass

        self.ip_address_hotspot.text = network_ip

    def render(self, image):
        self.draw_info_image(image)
        self.draw_wifi_strength(image)
        self.draw_info_text(image)
