from components.widgets.common_functions import title_text, get_font, align_to_middle
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        screen_text = "www.pi-top.com/gettingstarted"
        title_text(draw, 3, width, text="GOTO")
        draw.text(
            (align_to_middle(draw, width, screen_text) + 27, height / 2),
            text=screen_text,
            font=get_font(8),
            fill="white",
        )
