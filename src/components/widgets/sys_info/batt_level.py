# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.sys_info import get_battery
from os import path
from PIL import Image, ImageFont
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
        draw.text(
            xy=(0 * width / 4, 0 * height / 4),
            text=get_battery(),
            font=self.font,
            fill="white",
        )
        img_path = path.abspath(
            path.join(path.dirname(__file__), "assets", "battery.png")
        )
        img_bitmap = Image.open(img_path).convert("RGBA")
        draw.bitmap(xy=(1 * width / 2, 0 * height / 2), bitmap=img_bitmap, fill="white")
