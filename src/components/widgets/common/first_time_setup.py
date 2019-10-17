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
        self.gif = ImageComponent(
            image_path=get_image_file("first_time_connect.gif"), loop=True, playback_speed=1.0)

        self.ptusb0_ip = ""
        self.connected_device_ip = ""
        self.initialised = False

        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top"

        self.is_moving_to_show_data = True
        self.finished = False

        self.x = 0

        self.default_interval = self.interval

    def reset(self):
        self.gif = ImageComponent(
            image_path=get_image_file("first_time_connect.gif"), loop=True, playback_speed=1.0)

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

        self.is_moving_to_show_data = self.is_connected() and not self.x <= -128
        self.initialised = True

    def gif_is_off_screen(self):
        return self.x <= -128

    def render(self, draw, width, height):
        # Determine connection state
        if not self.is_moving_to_show_data:
            self.set_data_members()

        self.gif.hold_first_frame = self.is_connected()

        if self.is_moving_to_show_data:
            self.interval = 0.025

            # Move GIF to the left
            self.x -= 5

            # Stop moving GIF to the left if off screen
            if self.gif_is_off_screen:
                self.is_moving_to_show_data = False
        else:
            if not self.is_connected():
                # Reset GIF position
                self.x = 0
            self.interval = self.default_interval

        # Draw to OLED
        self.gif.xy = (self.x, 0)
        self.gif.render(draw)

        show_data = \
            self.is_connected() and \
            not self.is_moving_to_show_data and \
            self.gif_is_off_screen()

        if show_data:
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
