import PIL.Image
import PIL.ImageDraw
from pitop.common.sys_info import get_ap_mode_status
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...utils import get_image_file_path
from ..base import PageBase
from .values import (
    common_first_line_y,
    common_second_line_y,
    common_third_line_y,
    default_margin_x,
)


class Page(PageBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.info_image = PIL.Image.open(
            get_image_file_path("sys_info/networking/ap_info.png")
        )

    def draw_info_image(self, image):
        draw = PIL.ImageDraw.Draw(image)

        draw.bitmap(
            xy=(0, 0),
            bitmap=self.info_image,
            fill="white",
        )

    def draw_info_text(self, image):
        ap_data = get_ap_mode_status()

        assistant = MiniscreenAssistant("1", (128, 64))
        assistant.render_text(
            image,
            text=ap_data.get("ssid", ""),
            font_size=12,
            xy=(default_margin_x, common_first_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

        assistant.render_text(
            image,
            text=ap_data.get("passphrase", ""),
            font_size=12,
            xy=(default_margin_x, common_second_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

        assistant.render_text(
            image,
            text=ap_data.get("ip_address", ""),
            font_size=12,
            xy=(default_margin_x, common_third_line_y),
            align="left",
            anchor="lm",
            wrap=False,
        )

    def render(self, image):
        self.draw_info_image(image)
        self.draw_info_text(image)
