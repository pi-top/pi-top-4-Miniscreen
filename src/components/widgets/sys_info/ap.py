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

from enum import Enum
from PIL import Image


class RenderState(Enum):
    STATIONARY = 0
    ANIMATING = 1
    DISPLAYING_INFO = 2


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.mode = mode

        self.title_image_pos = (0, 0)

        self.title_connected_image = process_image(
            Image.open(get_image_file_path("sys_info/ap_title.png"))
        )

        def add_disconnected_icon(pil_image):
            pil_image_disconnected_draw = ImageDraw.Draw(pil_image)
            pil_image_disconnected_draw.ellipse((70, 23) + (84, 37), 0, 0)
            pil_image_disconnected_draw.ellipse((71, 24) + (83, 36), 1, 0)
            pil_image_disconnected_draw.line((74, 27) + (79, 32), "black", 2)
            pil_image_disconnected_draw.line((75, 32) + (80, 27), "black", 2)

        self.title_disconnected_image = self.title_connected_image.copy()
        add_disconnected_icon(self.title_disconnected_image)

        self.info_image = process_image(
            Image.open(get_image_file_path("sys_info/ap_info.png"))
        )

        self.default_interval = interval

        self.ssid = ""
        self.wlan0_ip = ""
        self.passphrase = ""
        self.initialised = False

        self.interval = self.default_interval

        self.render_state = RenderState.STATIONARY

    def process_image(self, image_to_process):
        if image_to_process.size == self.size:
            image = image_to_process
            if image.mode != self.mode:
                image = image.convert(self.mode)
        else:
            image = Image.new(
                self.mode,
                self.size,
                "black"
            )
            image.paste(
                image_to_process.resize(
                    self.size,
                    resample=Image.NEAREST
                )
            )

        return image

    def reset(self):
        self.reset_animation()
        self.reset_data_members()

    def reset_animation(self):
        self.title_image_pos = (0, 0)
        self.render_state = RenderState.STATIONARY

    def reset_data_members(self):
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
            self.reset_animation()

        self.initialised = True

    def set_interval(self):
        if self.render_state == RenderState.STATIONARY:
            self.interval = 0.5
        else:
            if self.render_state == RenderState.ANIMATING
            self.interval = 0.025
            else:
                self.interval = self.default_interval

    def update_render_state(self):
        if self.is_connected():
            if self.title_image_pos[0] <= -self.width:
                self.render_state = RenderState.DISPLAYING_INFO

            elif self.render_state != RenderState.DISPLAYING_INFO:
                self.render_state = RenderState.ANIMATING
                self.title_image_pos = (self.title_image_pos[0] - 1, 0)
        else:
            self.reset_animation()

    def render(self, draw, width, height):
        # Determine connection state
        if not self.initialised or self.render_state == RenderState.DISPLAYING_INFO:
            self.set_data_members()

        self.update_render_state()

        if self.render_state == RenderState.DISPLAYING_INFO:
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
        else:
            title_image = self.title_connected_image if self.is_connected() \
                else self.title_disconnected_image

            draw.bitmap(
                xy=self.title_image_pos,
                bitmap=title_image,
                fill="white",
            )

        self.set_interval()
