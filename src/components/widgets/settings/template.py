from components.widgets.common_functions import get_file
from components.widgets.common_values import default_margin_y
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.type = data.get("type")
        self.method = data.get("method")

    def get_image(self):
        state = self.method()

        if state == "enabled":
            return get_file("settings_pages/" + self.type + "_on.gif")
        else:
            return get_file("settings_pages/" + self.type + "_off.gif")

    def render(self, draw, width, height):
        self.gif = ImageComponent(image_path=self.get_image(), loop=False)
        self.gif.render(draw)
