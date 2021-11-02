from getpass import getuser
from ipaddress import ip_address

import PIL.Image
import PIL.ImageDraw
from pitop.common.pt_os import is_pi_using_default_password
from pitop.common.sys_info import get_internal_ip
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...utils import get_image_file_path
from ..base import Page as PageBase
from .base import (
    common_first_line_y,
    common_second_line_y,
    common_third_line_y,
    default_margin_x,
)


class Page(PageBase):
    def __init__(self, interval, size, mode, config, offset):
        super().__init__(
            interval=interval, size=size, mode=mode, config=config, offset=offset
        )
        self.info_image = PIL.Image.open(
            get_image_file_path("sys_info/networking/usb_info.png")
        )

    def draw_info_image(self, image):
        draw = PIL.ImageDraw.Draw(image)

        draw.bitmap(
            xy=(0, 0),
            bitmap=self.info_image,
            fill="white",
        )

    def draw_info_text(self, image):
        user = "pi" if getuser() == "root" else getuser()

        password = "pi-top" if is_pi_using_default_password() is True else "********"

        ip_addr = ""
        try:
            ip_addr = ip_address(get_internal_ip(iface="ptusb0"))
        except ValueError:
            pass

        assistant = MiniscreenAssistant("1", (128, 64))
        assistant.render_text(
            image,
            text=user,
            font_size=12,
            xy=(default_margin_x, common_first_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

        assistant.render_text(
            image,
            text=password,
            font_size=12,
            xy=(default_margin_x, common_second_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

        assistant.render_text(
            image,
            text=ip_addr,
            font_size=12,
            xy=(default_margin_x, common_third_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

    def render(self, image):
        self.draw_info_image(image)
        self.draw_info_text(image)
