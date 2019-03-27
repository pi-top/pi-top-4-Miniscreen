from ptcommon.sys_info import get_battery_capacity, get_battery_charging_state
from components.widgets.common_functions import draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_functions import get_file
from components.widgets.common.image_component import ImageComponent


def draw_battery_percentage(draw, width, height):
    percentage = int(get_battery_capacity()[:1])
    top_margin = 25
    bottom_margin = 38
    left_margin = 14
    bar_width = left_margin + int(50 * (percentage / 100))
    draw.rectangle(
        (left_margin, top_margin) + (bar_width, bottom_margin), "white", "white"
    )


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            image_path=get_file("battery_shell_empty.gif"), loop=False
        )

    def render(self, draw, width, height):
        x_margin = 69
        y_margin = 21
        if get_battery_charging_state() == "charging":
            battery_state = get_file("battery_shell_charging.gif")
        else:
            battery_state = get_file("battery_shell_empty.gif")
            draw_battery_percentage(draw, width, height)
        self.gif = ImageComponent(image_path=battery_state, loop=False)
        self.gif.render(draw)
        draw_text(
            draw, xy=(x_margin, y_margin), text=get_battery_capacity(), font_size=18
        )
