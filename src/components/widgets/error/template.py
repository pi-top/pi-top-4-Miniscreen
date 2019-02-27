from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_functions import draw_text


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")
        self.second_line = data.get("second_line")

    def render(self, draw, width, height):
        text_width, text_height = draw.textsize(self.title)
        draw_text(
            draw,
            xy=(width / 2 - text_width / 2,
            height / 4 - text_height / 4),
            text=self.title,
        )
        text_width, text_height = draw.textsize(self.second_line)
        draw_text(
            draw,
            xy=(width / 2 - text_width / 2,
            height / 2 - text_height / 2),
            text=self.second_line,
        )
