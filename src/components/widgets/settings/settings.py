from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_functions import draw_text
from components.widgets.common_functions import get_file
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(image_path=get_file("settings_page.gif"), loop=True)
        self.title = data.get("title")

    def render(self, draw, width, height):
        self.gif.render(draw)
        x_margin = 45
        y_margin = 19
        draw_text(draw, xy=(x_margin, y_margin), text=self.title, font_size=18)
