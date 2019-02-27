from ptcommon.sys_info import get_battery_capacity, get_battery_charging_state
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

    def render(self, draw, width, height):
        draw_text(draw, xy=(5, height / 5), text="Capacity: " + get_battery_capacity())
        draw_text(
            draw, xy=(5, height / 2), text=get_battery_charging_state(), font=self.font
        )
