from ptcommon.sys_info import get_internal_ip
from components.widgets.common.functions import draw_text, get_image_file
from components.widgets.common.values import (
    default_margin_y,
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent
from ipaddress import ip_address


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            image_path=get_image_file("sys_info/lan_page.gif"), loop=False, playback_speed=2.0)

        self.eth0_ip = ""
        self.initialised = False

        self.default_interval = self.interval

    def reset(self):
        self.gif = ImageComponent(
            image_path=get_image_file("sys_info/lan_page.gif"),
            loop=False,
            playback_speed=2.0,
        )

        self.eth0_ip = ""
        self.initialised = False

        self.interval = self.default_interval

    def is_connected(self):
        return self.eth0_ip != ""

    def set_data_members(self):
        try:
            self.eth0_ip = ip_address(get_internal_ip(iface="eth0"))
        except ValueError:
            self.eth0_ip = ""

        if not self.is_connected():
            self.gif = ImageComponent(
                image_path=get_image_file("sys_info/lan_page.gif"),
                loop=False,
                playback_speed=2.0,
            )

        self.gif.hold_first_frame = not self.is_connected()
        self.initialised = True

    def render(self, draw, width, height):
        first_frame = not self.initialised

        # Determine initial connection state
        if first_frame:
            self.set_data_members()

        # Determine connection state
        if not self.gif.is_animating():
            self.set_data_members()

        # Determine animation speed
        # TODO: fix frame speed in GIF
        # self.interval = self.gif.frame_duration
        if first_frame:
            self.interval = 0.5
        else:
            if self.gif.is_animating():
                self.interval = 0.025
            else:
                self.interval = self.default_interval

        # Draw to OLED
        self.gif.render(draw)

        if self.initialised and not self.gif.is_animating():
            if self.is_connected() and self.gif.finished:
                draw_text(
                    draw, xy=(default_margin_x, common_second_line_y), text=str(
                        self.eth0_ip)
                )
            elif not self.is_connected() and self.gif.hold_first_frame:
                draw.ellipse((69, 21) + (83, 35), 0, 0)
                draw.ellipse((70, 22) + (82, 34), 1, 0)
                draw.line((73, 25) + (78, 30), "black", 2)
                draw.line((74, 30) + (79, 25), "black", 2)
