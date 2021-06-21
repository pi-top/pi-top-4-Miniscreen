from pitopcommon.sys_info import get_ap_mode_status
from components.widgets.common.functions import draw_text, get_image_file_path
from components.widgets.common.values import (
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widgets import BaseSnapshot
from components.widgets.common.image_component import ImageComponent
from ipaddress import ip_address


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.width = width
        self.height = height
        self.mode = mode
        self.gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("sys_info/ap.gif"),
            loop=False,
            playback_speed=2.0,
        )

        self.ssid = ""
        self.wlan0_ip = ""
        self.passphrase = ""
        self.initialised = False

        self.default_interval = interval

    def reset(self):
        self.gif = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("sys_info/ap.gif"),
            loop=False,
            playback_speed=2.0,
        )

        self.ssid = ""
        self.wlan0_ip = ""
        self.passphrase = ""
        self.initialised = False

        self.interval = self.default_interval

    def is_connected(self):
        return self.wlan0_ip != "" and self.ssid != ""

    def set_data_members(self):
        ap_data = get_ap_mode_status()
        self.ssid = ap_data.get("ssid", "")
        self.wlan0_ip = ap_data.get("ip_address", "")
        self.passphrase = ap_data.get("passphrase", "")

        if not self.is_connected():
            self.gif = ImageComponent(
                device_mode=self.mode,
                width=self.width,
                height=self.height,
                image_path=get_image_file_path("sys_info/ap.gif"),
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

        ap_state = get_ap_mode_status()
        if self.initialised and not self.gif.is_animating():
            if self.is_connected() and self.gif.finished:
                draw_text(
                    draw,
                    xy=(default_margin_x, common_first_line_y),
                    text=str(self.ssid),
                )
                draw_text(
                    draw,
                    xy=(default_margin_x, common_second_line_y),
                    text=str(self.passphrase),
                )
                draw_text(
                    draw,
                    xy=(default_margin_x, common_third_line_y),
                    text=str(self.wlan0_ip)
                )
            elif not self.is_connected() and self.gif.hold_first_frame:
                draw.ellipse((70, 23) + (84, 37), 0, 0)
                draw.ellipse((71, 24) + (83, 36), 1, 0)
                draw.line((74, 27) + (79, 32), "black", 2)
                draw.line((75, 32) + (80, 27), "black", 2)
