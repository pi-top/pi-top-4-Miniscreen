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
import subprocess
from isc_dhcp_leases import Lease, IscDhcpLeases


def get_dhcp_leases():
    leases = IscDhcpLeases('/var/lib/dhcp/dhcpd.leases')
    return leases.get_current()


def ping(address):
    return subprocess.call(['fping', '-c1', '-t100', str(address)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_active_dhcp_lease_ip():
    current_leases_dict = get_dhcp_leases()
    for lease in current_leases_dict.values():
        address = lease.ip
        response = ping(address)
        if response == 0:
            return address
    return ""


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            image_path=get_image_file("vnc_page.gif"), loop=False, playback_speed=2.0)
        self.counter = 0

        self.ptusb0_ip = "Disconnected"
        self.username = "pi" if getuser() == "root" else getuser()
        self.password = "pi-top"
        self.current_lease_ip = ""
        self.is_connected = False
        self.initialised = False

        self.default_interval = self.interval

    def reset(self):
        self.gif = ImageComponent(
            image_path=get_image_file("vnc_page.gif"), loop=False, playback_speed=2.0)

        self.ptusb0_ip = "Disconnected"
        self.current_lease_ip = ""
        self.is_connected = False
        self.initialised = False

    def set_vnc_data_members(self):
        def _is_connected():
            return self.current_lease_ip != "" and ping(self.current_lease_ip) == 0

        try:
            self.ptusb0_ip = ip_address(get_internal_ip(iface="ptusb0"))
        except ValueError:
            self.ptusb0_ip = "Disconnected"

        if not self.is_connected:
            self.current_lease_ip = get_active_dhcp_lease_ip()
        self.is_connected = _is_connected()
        self.initialised = True

    def render(self, draw, width, height):
        if self.gif.frame_duration is None or not self.is_animating():
            self.set_vnc_data_members()

        self.gif.hold_first_frame = not self.is_connected

        self.gif.render(draw)

        # If GIF is still playing, update refresh time based on GIF's current frame length
        # Otherwise, set to originally defined interval for refreshing data members
        self.interval = (
            self.default_interval if self.gif.finished else self.gif.frame_duration
        )

        if self.gif.finished is True:
            if self.is_connected:
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
            else:
                if self.initialised:
                    draw.line((30, 10) + (98, 54), "white", 2)
                self.reset()
