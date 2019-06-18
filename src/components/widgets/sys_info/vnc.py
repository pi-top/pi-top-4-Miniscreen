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
            image_path=get_image_file("vnc_page.gif"), loop=False)
        self.counter = 0

        self.eth0_ip = ""
        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top"

    def reset(self):
        self.gif = ImageComponent(
            image_path=get_image_file("vnc_page.gif"), loop=False)
        self.counter = 0

    def set_vnc_data_members(self):
        try:
            self.eth0_ip = ip_address(get_internal_ip(iface="eth0"))
        except ValueError:
            self.eth0_ip = ""

    def render(self, draw, width, height):
        self.gif.render(draw)

        if self.gif.finished is True:
            if self.counter == 0:
                self.set_vnc_data_members()
                self.counter = 10
            self.counter -= 1

            draw_text(
                draw, xy=(default_margin_x, common_first_line_y), text=str(
                    self.eth0_ip)
            )
            draw_text(
                draw,
                xy=(default_margin_x, common_second_line_y),
                text=str(self.username),
            )
            draw_text(
                draw,
                xy=(default_margin_x, common_third_line_y),
                text=str(self.password),
            )
