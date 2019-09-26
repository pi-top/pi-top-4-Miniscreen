from ptcommon.sys_info import get_internal_ip
from components.widgets.common_functions import title_text, draw_text, get_image_file
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent
from components.widgets.common_values import (
    default_margin_y,
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from getpass import getuser
from ipaddress import ip_address


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            image_path=get_image_file("lan_page.gif"), loop=False, playback_speed=2.0)
        self.counter = 0

        self.eth0_ip = "Disconnected"

        self.default_interval = self.interval

    def reset(self):
        self.gif = ImageComponent(
            image_path=get_image_file("lan_page.gif"), loop=False, playback_speed=2.0)
        self.counter = 0

    def set_eth0_data_members(self):
        try:
            self.eth0_ip = ip_address(get_internal_ip(iface="eth0"))
        except ValueError:
            self.eth0_ip = "Disconnected"

    def render(self, draw, width, height):
        self.gif.render(draw)

        # If GIF is still playing, update refresh time based on GIF's current frame length
        # Otherwise, set to originally defined interval for refreshing data members
        self.interval = (
            self.default_interval if self.gif.finished else self.gif.frame_duration
        )

        if self.gif.finished is True:
            if self.counter == 0:
                self.set_eth0_data_members()
                self.counter = 10
            self.counter -= 1

            draw_text(
                draw, xy=(default_margin_x, common_second_line_y), text=str(
                    self.eth0_ip))
