from components.widgets.common.base_widgets import BaseSnapshot
from components.widgets.common.functions import draw_text, get_image_file_path
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            device_mode=mode,
            width=width,
            height=height,
            image_path=get_image_file_path("menu/settings.gif"),
            loop=True,
        )
        self.title = data.get("title")

    def render(self, draw, width, height):
        self.gif.render(draw)
        x_margin = 45
        y_margin = 19
        draw_text(draw, xy=(x_margin, y_margin), text=self.title, font_size=18)
