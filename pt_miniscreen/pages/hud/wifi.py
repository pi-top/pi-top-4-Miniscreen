from ipaddress import ip_address

import PIL.Image
import PIL.ImageDraw
from pitop.common.sys_info import (
    get_internal_ip,
    get_network_strength,
    get_wifi_network_ssid,
)
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

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
        assistant = MiniscreenAssistant("1", (128, 64))
        assistant.render_text(
            image,
            text=get_wifi_network_ssid(),
            font_size=12,
            xy=(default_margin_x, common_second_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

        network_ip = ""
        try:
            network_ip_candidate = get_internal_ip(iface="wlan0")
            ip_address(network_ip_candidate)
            network_ip = network_ip_candidate

        except ValueError:
            pass

        assistant.render_text(
            image,
            text=network_ip,
            font_size=12,
            xy=(default_margin_x, common_third_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

    def render(self, image):
        self.draw_info_image(image)
        self.draw_wifi_strength(image)
        self.draw_info_text(image)
