import PIL.ImageDraw
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...menu_base import MenuBase


class Menu(MenuBase):
    def __init__(self, size, mode, redraw_speed, config):
        def overlay(image):
            title_overlay_h = 19

            # Empty the top of the image
            PIL.ImageDraw.Draw(image).rectangle(
                ((0, 0), (size[0], title_overlay_h)), fill=1
            )

            # 1px overlay separator
            PIL.ImageDraw.Draw(image).rectangle(
                ((0, title_overlay_h), (size[0], title_overlay_h)), fill=0
            )

            asst = MiniscreenAssistant(mode, size)
            asst.render_text(
                image,
                xy=(size[0] / 2, size[1] / 6),
                text="C O N N E C T I O N",
                wrap=False,
                font=asst.get_mono_font_path(bold=True),
                fill=0,
            )

        super().__init__(
            size,
            mode,
            redraw_speed,
            overlay_render_func=overlay,
            config=config,
        )
