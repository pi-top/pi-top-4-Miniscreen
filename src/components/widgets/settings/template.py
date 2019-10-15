from components.widgets.common_functions import get_image_file
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.type = data.get("type")
        self.get_state_method = data.get("get_state_method")

    def get_image(self):
        if self.get_state_method is not None:
            state = self.get_state_method()
            if state == "Enabled":
                return get_image_file("settings_pages/" + self.type + "_on.gif")
            else:
                return get_image_file("settings_pages/" + self.type + "_off.gif")
        else:
            return get_image_file("settings_pages/" + self.type + ".gif")

    def render(self, draw, width, height):
        self.gif = ImageComponent(image_path=self.get_image(), loop=False)
        self.gif.render(draw)
