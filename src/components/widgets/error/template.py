from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")
        self.second_line = data.get("second_line")

    def render(self, draw, width, height):
        text_width, text_height = draw.textsize(self.title)
        draw.text(
            (width / 2 - text_width / 2, height / 4 - text_height / 4),
            text=self.title,
            fill="white",
        )
        text_width, text_height = draw.textsize(self.second_line)
        draw.text(
            (width / 2 - text_width / 2, height / 2 - text_height / 2),
            text=self.second_line,
            fill="white",
        )
