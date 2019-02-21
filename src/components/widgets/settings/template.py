from components.widgets.common_functions import title_text, tiny_font
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")
        self.method = data.get("method")
        print(self.method)

    def render(self, draw, width, height):
        margin = 3
        title_text(draw, margin, width, text=self.title)
        draw.text(
            (width / 3, 30), text=str(self.method()), font=tiny_font, fill="white"
        )
