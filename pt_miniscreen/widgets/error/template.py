from pt_miniscreen.widgets.common import BaseHotspot, align_to_middle, draw_text


class Hotspot(BaseHotspot):
    def __init__(self, width, height, mode, **data):
        super(Hotspot, self).__init__(width, height, self.render)

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
