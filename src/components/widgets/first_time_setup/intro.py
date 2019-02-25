from components.widgets.common_functions import title_text, really_tiny_font, align_to_middle
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        intro_text = "Connect to a screen"
        screen_text = "or press down and connect via"
        vnc_text = "VNC"

        title_text(draw, 3, width, text="Welcome")

        draw.text(
            (align_to_middle(draw, width, intro_text) + 15, 20),
            text=intro_text,
            font=really_tiny_font,
            fill="white",
        )
        draw.text(
            (align_to_middle(draw, width, screen_text) + 27, 35),
            text=screen_text,
            font=really_tiny_font,
            fill="white",
        )
        draw.text(
            (align_to_middle(draw, width, vnc_text), 50),
            text=vnc_text,
            font=really_tiny_font,
            fill="white",
        )
