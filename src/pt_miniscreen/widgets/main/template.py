from .widgets.common import BaseHotspot, draw_text


class Hotspot(BaseHotspot):
    def __init__(self, width, height, mode, **data):
        super(Hotspot, self).__init__(width, height, self.render)

        self.title = data.get("title")

    def render(self, draw, width, height):
        text_width, text_height = draw.textsize(self.title)
        draw_text(
            draw,
            xy=(width / 2 - text_width / 2, height / 2 - text_height / 2),
            text=self.title,
        )
