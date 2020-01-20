from ptcommon.sys_info import get_internal_ip
from ptcommon.pt_os import is_pi_using_default_password
from components.widgets.common_functions import draw_text, get_image_file
from components.widgets.common_values import (
    default_margin_y,
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent
from components.widgets.network_helpers import get_address_for_ptusb_connected_device
from getpass import getuser
from ipaddress import ip_address


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.usb_gif = ImageComponent(
            image_path=get_image_file("usb_page.gif"), loop=False, playback_speed=2.0)
        self.connect_gif = ImageComponent(
            image_path=get_image_file("first_time_connect.gif"), loop=True, playback_speed=1.0)

        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top" if is_pi_using_default_password() is True else "********"

        self.default_interval = self.interval

    def reset(self):
        self.usb_gif = ImageComponent(
            image_path=get_image_file("usb_page.gif"), loop=False, playback_speed=2.0)

        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.interval = self.default_interval

    def is_connected(self):
        return self.connected_device_ip != ""

    def set_data_members(self):
        try:
            self.ptusb0_ip = ip_address(get_internal_ip(iface="ptusb0"))
        except ValueError:
            self.ptusb0_ip = ""

        self.connected_device_ip = get_address_for_ptusb_connected_device()

        if not self.is_connected():
            self.usb_gif = ImageComponent(
                image_path=get_image_file("usb_page.gif"),
                loop=False,
                playback_speed=2.0,
            )

        self.usb_gif.hold_first_frame = not self.is_connected()
        self.initialised = True

    def render(self, draw, width, height):
        first_frame = not self.initialised

        # Determine initial connection state
        if first_frame:
            self.set_data_members()

        # Determine connection state
        if not self.usb_gif.is_animating():
            self.set_data_members()

        # Determine animation speed
        # TODO: fix frame speed in GIF
        # self.interval = self.usb_gif.frame_duration
        if not self.is_connected():
            self.interval = 0.5
        else:
            if self.usb_gif.is_animating():
                self.interval = 0.025
            else:
                self.interval = self.default_interval

        # Draw to OLED
        if not self.is_connected():
            self.connect_gif.render(draw)
        else:
            self.usb_gif.render(draw)

        if self.initialised and not self.usb_gif.is_animating():
            if self.is_connected() and self.usb_gif.finished:
                draw_text(
                    draw,
                    xy=(default_margin_x, common_first_line_y),
                    text=str(self.username),
                )
                draw_text(
                    draw,
                    xy=(default_margin_x, common_second_line_y),
                    text=str(self.password),
                )
                draw_text(
                    draw,
                    xy=(default_margin_x, common_third_line_y),
                    text=str(self.ptusb0_ip)
                )
