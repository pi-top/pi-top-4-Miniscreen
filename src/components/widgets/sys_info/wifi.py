from ptcommon.sys_info import get_network_id, get_internal_ip, get_ssh_enabled_state
from components.widgets.common_functions import draw_text, get_file
from components.widgets.common_values import (
    default_margin_x,
    default_margin_y,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent
import os


def get_wifi_strength():
    try:
        response = os.popen('iwconfig wlan0 | grep "Link Quality="').read()
        wifi_strngeth_as_string = response.split("=")[1].split(" ")[0]
        strength, max = wifi_strngeth_as_string.split("/")
        return int(strength) / int(max)
    except:
        return 0


def wifi_strength_rating():
    wifi_strength = get_wifi_strength()
    if wifi_strength <= 0.4:
        wifi_rating = "BAD"
    elif 0.4 < wifi_strength <= 0.6:
        wifi_rating = "OKAY"
    else:
        wifi_rating = "EXCELLENT"
    return wifi_rating


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(image_path=get_file("wifi_page.gif"), loop=False)

    def render(self, draw, width, height):
        self.gif.render(draw)
        wifi_id = get_network_id() if get_network_id() is not "TEST" else "NO WIFI"
        if self.gif.finished is True:

            draw_text(
                draw,
                xy=(default_margin_x, common_first_line_y),
                text=str(wifi_strength_rating()),
            )
            draw_text(
                draw,
                xy=(default_margin_x, common_second_line_y),
                text=str(wifi_id),
            )
            draw_text(
                draw,
                xy=(default_margin_x, common_third_line_y),
                text=str(get_internal_ip()),
            )
