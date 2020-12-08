from .components.widgets.common.base_widget_hotspot import BaseHotspot
from .components.widgets.common.functions import draw_text, align_to_middle


class Hotspot(BaseHotspot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")
        self.second_line = data.get("second_line")

    def render(self, draw, width, height):
        text_width, text_height = draw.textsize(self.title)
        draw_text(
            draw,
            xy=(
                align_to_middle(draw, width, text=self.title),
                height / 4 - text_height / 4,
            ),
            text=self.title,
        )
        text_width, text_height = draw.textsize(self.second_line)
        draw_text(
            draw,
            xy=(
                align_to_middle(draw, width, text=self.title),
                height / 1.5 - text_height / 2,
            ),
            text=self.second_line,
        )
