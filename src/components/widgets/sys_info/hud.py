from ptcommon.sys_info import (
    get_cpu_percentage,
    get_network_strength,
    get_battery_capacity,
    get_temperature,
)
from os import path
from PIL import Image, ImageFont
from components.widgets.common_functions import draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.font = ImageFont.truetype(
            path.abspath(
                path.join(
                    path.dirname(__file__),
                    "..",
                    "..",
                    "..",
                    "fonts",
                    "C&C Red Alert [INET].ttf",
                )
            ),
            size=12,
        )

    # TODO: Fix images loading correctly
    def render(self, draw, width, height):
        draw_text(
            draw,
            xy=(0 * width / 4,
            0 * height / 4),
            text=get_battery_capacity(),
            font=self.font,
        )
        img_path = path.abspath(
            path.join(path.dirname(__file__), "assets", "battery.png")
        )
        img_bitmap = Image.open(img_path).convert("RGBA")
        draw.bitmap(xy=(1 * width / 4, 0 * height / 4), bitmap=img_bitmap, fill="white")

        draw_text(
            draw,
            xy=(2 * width / 4,
            0 * height / 4),
            text=get_network_strength("wlan0"),
            font=self.font,
        )
        img_path = path.abspath(
            path.join(path.dirname(__file__), "assets", "wifi_icon.png")
        )
        img_bitmap = Image.open(img_path).convert("RGBA")
        draw.bitmap(xy=(3 * width / 4, 0 * height / 4), bitmap=img_bitmap, fill="white")

        draw_text(
            draw,
            xy=(0 * width / 4,
            2 * height / 4),
            text=get_cpu_percentage(),
            font=self.font,
        )
        img_path = path.abspath(path.join(path.dirname(__file__), "assets", "cpu.png"))
        img_bitmap = Image.open(img_path).convert("RGBA")
        draw.bitmap(xy=(1 * width / 4, 2 * height / 4), bitmap=img_bitmap, fill="white")

        draw_text(
            draw,
            xy=(2 * width / 4,
            2 * height / 4),
            text=get_temperature(),
            font=self.font,
        )
        img_path = path.abspath(
            path.join(path.dirname(__file__), "assets", "thermometer.png")
        )
        img_bitmap = Image.open(img_path).convert("RGBA")
        draw.bitmap(xy=(3 * width / 4, 2 * height / 4), bitmap=img_bitmap, fill="white")
