from ptcommon.sys_info import get_internal_ip
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
from getpass import getuser
from ipaddress import ip_address
import subprocess
from isc_dhcp_leases import IscDhcpLeases


def get_connected_device_ip():
    current_leases_dict = IscDhcpLeases(
        '/var/lib/dhcp/dhcpd.leases').get_current()
    for lease in current_leases_dict.values():
        address = lease.ip
        response = subprocess.call(['fping', '-c1', '-t100', str(address)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if response == 0:
            return address
    return ""


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.vnc_gif = ImageComponent(
            image_path=get_image_file("vnc_page.gif"), loop=False, playback_speed=2.0)
        self.connect_gif = ImageComponent(
            image_path=get_image_file("first_time_connect.gif"), loop=True, playback_speed=2.0)

        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top"

        self.default_interval = self.interval

    def reset(self):
        self.vnc_gif = ImageComponent(
            image_path=get_image_file("vnc_page.gif"), loop=False, playback_speed=2.0)

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

        self.connected_device_ip = get_connected_device_ip()

        if not self.is_connected():
            self.vnc_gif = ImageComponent(
                image_path=get_image_file("vnc_page.gif"),
                loop=False,
                playback_speed=2.0,
            )
        self.initialised = True

    def render(self, draw, width, height):
        first_frame = not self.initialised

        # Determine initial connection state
        if first_frame:
            self.set_data_members()

        # Determine connection state
        if not self.vnc_gif.is_animating():
            self.set_data_members()

        # Determine animation speed
        # TODO: fix frame speed in GIF
        # self.interval = self.vnc_gif.frame_duration
        if first_frame:
            self.interval = 0.5
        else:
            if self.vnc_gif.is_animating():
                self.interval = 0.025
            else:
                self.interval = self.default_interval

        # Draw to OLED
        if not self.is_connected():
            self.connect_gif.render(draw)
        else:
            self.vnc_gif.render(draw)

        if self.initialised and not self.vnc_gif.is_animating():
            if self.is_connected() and self.vnc_gif.finished:
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
