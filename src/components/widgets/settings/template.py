from components.widgets.common_functions import title_text, draw_text
from components.widgets.common_values import top_margin
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")
        self.method = data.get("method")

    def render(self, draw, width, height):
        title_text(draw, top_margin, width, text=self.title)
        draw_text(draw, xy=(width / 3, 30), text=str(self.method()))
