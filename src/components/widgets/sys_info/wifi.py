from ptcommon.sys_info import get_network_id, get_internal_ip, get_network_strength
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


def wifi_strength_image():
    wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100
    wifi_rating = "wifi_strength_bars/"
    if wifi_strength == 0:
        wifi_rating += "wifi_no_signal.gif"
    elif 0 < wifi_strength <= 0.5:
        wifi_rating += "wifi_weak_signal.gif"
    elif 0.4 < wifi_strength <= 0.6:
        wifi_rating += "wifi_okay_signal.gif"
    elif 0.6 < wifi_strength <= 0.7:
        wifi_rating += "wifi_good_signal.gif"
    else:
        wifi_rating += "wifi_excellent_signal.gif"
    return get_file(wifi_rating)


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(image_path=get_file("wifi_page.gif"), loop=False)

    def render(self, draw, width, height):
        self.gif.render(draw)
        wifi_id = get_network_id() if get_network_id() is not "TEST" else "NO WIFI"
        if self.gif.finished is True:

            self.wifi_bars = ImageComponent(
                xy=(5, 0), image_path=wifi_strength_image(), loop=True
            )
            self.wifi_bars.render(draw)
            draw_text(
                draw, xy=(default_margin_x, common_second_line_y), text=str(wifi_id)
            )
            draw_text(
                draw,
                xy=(default_margin_x, common_third_line_y),
                text=str(get_internal_ip()),
            )
