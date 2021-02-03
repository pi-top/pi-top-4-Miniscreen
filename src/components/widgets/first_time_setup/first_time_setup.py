from getpass import getuser
from ipaddress import ip_address

from pitopcommon.sys_info import (
    get_internal_ip,
    get_address_for_ptusb_connected_device
)
from pitopcommon.pt_os import is_pi_using_default_password
from components.widgets.common.functions import draw_text, get_image_file_path
from components.widgets.common.values import (
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widgets import BaseSnapshot
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.width = width
        self.height = height
        self.mode = mode
        self.ethernet_gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("first_time_connect/lan_vnc.gif"),
            loop=False,
            playback_speed=2.0
        )
        self.usb_gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("sys_info/usb.gif"),
            loop=False,
            playback_speed=2.0
        )
        self.connect_gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path(
                "first_time_connect/first_time_connect.gif"),
            loop=True,
            playback_speed=1.0
        )

        self.eth0_ip = ""
        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top" if is_pi_using_default_password() is True else "********"

        self.default_interval = self.interval

    def reset(self):
        self.ethernet_gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("first_time_connect/lan_vnc.gif"),
            loop=False,
            playback_speed=2.0
        )
        self.usb_gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("sys_info/usb.gif"),
            loop=False,
            playback_speed=2.0
        )

        self.eth0_ip = ""
        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.interval = self.default_interval

    def is_connected(self):
        return self.ethernet_is_connected() or self.usb_is_connected()

    def ethernet_is_connected(self):
        return self.eth0_ip != ""

    def usb_is_connected(self):
        return self.connected_device_ip != ""

    def is_animating(self):
        return self.usb_gif.is_animating() or self.ethernet_gif.is_animating()

    def ethernet_finished_animating(self):
        return self.ethernet_is_connected() and self.ethernet_gif.finished

    def usb_finished_animating(self):
        return self.usb_is_connected() and self.usb_gif.finished

    def set_data_members(self):
        if not self.ethernet_is_connected():
            try:
                self.ptusb0_ip = ip_address(get_internal_ip(iface="ptusb0"))
            except ValueError:
                self.ptusb0_ip = ""

            self.connected_device_ip = get_address_for_ptusb_connected_device()

        if not self.usb_is_connected():
            self.usb_gif = ImageComponent(
                device_mode=self.mode,
                width=self.width,
                height=self.height,
                image_path=get_image_file_path("sys_info/usb.gif"),
                loop=False,
                playback_speed=2.0,
            )
            try:
                self.eth0_ip = ip_address(get_internal_ip(iface="eth0"))
            except ValueError:
                self.eth0_ip = ""

        self.usb_gif.hold_first_frame = not self.usb_is_connected()

        if not self.ethernet_is_connected():
            self.ethernet_gif = ImageComponent(
                device_mode=self.mode,
                width=self.width,
                height=self.height,
                image_path=get_image_file_path(
                    "first_time_connect/lan_vnc.gif"),
                loop=False,
                playback_speed=2.0,
            )
        self.ethernet_gif.hold_first_frame = not self.ethernet_is_connected()

        self.initialised = True

    def render(self, draw, width, height):
        first_frame = not self.initialised

        # Determine initial connection state
        if first_frame:
            self.set_data_members()

        # Determine connection state
        if not self.is_animating():
            self.set_data_members()

        # Determine animation speed
        # TODO: fix frame speed in GIF
        # self.interval = self.usb_gif.frame_duration
        if not self.is_connected():
            self.interval = 0.5
        else:
            if self.is_animating():
                self.interval = 0.025
            else:
                self.interval = self.default_interval

        # Draw to OLED
        if self.usb_is_connected():
            self.usb_gif.render(draw)
        elif self.ethernet_is_connected():
            self.ethernet_gif.render(draw)
        else:
            self.connect_gif.render(draw)

        if self.initialised and not self.is_animating():
            if self.ethernet_finished_animating() or self.usb_finished_animating():
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
                    text=str(
                        self.ptusb0_ip if self.usb_finished_animating() else self.eth0_ip)
                )
