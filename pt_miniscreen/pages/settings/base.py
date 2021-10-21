from enum import Enum, auto

import PIL.ImageDraw
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...menu_base import MenuBase


class Page(Enum):
    CONNECTION = auto()


class Menu(MenuBase):
    def __init__(self, size, mode, redraw_speed, children):
        def overlay(image):
            title_overlay_h = 19

            # Empty the top of the image
            PIL.ImageDraw.Draw(image).rectangle(
                ((0, 0), (image.size[0], title_overlay_h)), fill=1
            )

            # 1px overlay separator
            PIL.ImageDraw.Draw(image).rectangle(
                ((0, title_overlay_h), (image.size[0], title_overlay_h)), fill=0
            )

            asst = MiniscreenAssistant(image.mode, image.size)
            asst.render_text(
                image,
                xy=(image.size[0] / 2, image.size[1] / 6),
                text="M E N U",
                wrap=False,
                font=asst.get_mono_font_path(bold=True),
                fill=0,
            )

        super().__init__(
            size,
            mode,
            redraw_speed,
            overlay_render_func=overlay,
            children=children,
        )
