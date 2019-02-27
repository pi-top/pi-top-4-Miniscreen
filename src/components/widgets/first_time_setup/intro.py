from components.widgets.common_functions import (
    title_text,
    get_font,
    align_to_middle,
    draw_text,
)
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        screen_text = "pi-top.com/start"
        title_text(draw, 3, width, text="Visit")
        draw_text(
            draw,
            xy=(align_to_middle(draw, width, screen_text) + width / 7,
            height / 2),
            text=screen_text,
            font=get_font(size=8),
        )
