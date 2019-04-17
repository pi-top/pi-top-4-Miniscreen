from components.widgets.common_functions import get_image_file
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.type = data.get("type")
        self.method = data.get("method")

    def get_image(self):
        state = self.method()
        if state == "Enabled":
            return get_image_file("settings_pages/" + self.type + "_on.gif")
        else:
            return get_image_file("settings_pages/" + self.type + "_off.gif")

    def render(self, draw, width, height):
        self.gif = ImageComponent(image_path=self.get_image(), loop=False)
        self.gif.render(draw)
