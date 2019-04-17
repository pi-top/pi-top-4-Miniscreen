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
from ipaddress import ip_address

def wifi_strength_image():
    wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100
    wifi_rating = "wifi_strength_bars/"
    if wifi_strength <= 0:
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
        self.reset()

    def reset(self):
        self.gif = ImageComponent(image_path=get_file("wifi_page.gif"), loop=False)
        self.counter = 0
        self.wifi_id = ""
        self.wlan0_ip = ""
        self.wifi_bars_image = ""

    def set_wifi_data_members(self):
        network_ssid = get_network_id()
        network_ip = get_internal_ip(iface="wlan0")
        network_ip = get_internal_ip(iface="eth0")
        try:
            self.wlan0_ip = ip_address(network_ip)
        except ValueError:
            self.wlan0_ip = ""
        self.wifi_id = network_ssid if network_ssid is not "Error" else "No WiFi"
        self.wifi_bars_image = wifi_strength_image()

    def render(self, draw, width, height):
        self.gif.render(draw)

        if self.counter == 10:
            self.set_wifi_data_members()
            self.counter = 0
        self.counter += 1

        if self.gif.finished is True:
            wifi_bars = ImageComponent(
                xy=(5, 0), image_path=self.wifi_bars_image, loop=True
            )
            wifi_bars.render(draw)

            draw_text(
                draw,
                xy=(default_margin_x, common_second_line_y),
                text=str(self.wifi_id),
            )

            draw_text(
                draw, xy=(default_margin_x, common_third_line_y), text=str(self.wlan0_ip)
            )
