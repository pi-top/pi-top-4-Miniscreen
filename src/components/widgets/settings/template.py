from components.widgets.common.functions import get_image_file_path
from components.widgets.common.base_widgets import BaseHotspot
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, mode, **data):
        super(Hotspot, self).__init__(width, height, self.render)

        self.width = width
        self.height = height
        self.mode = mode
        self.type = data.get("type")
        self.get_state_method = data.get("get_state_method")

    def get_image(self):
        if callable(self.get_state_method):
            if self.get_state_method() == "Enabled":
                return get_image_file_path("settings/" + self.type + "_on.gif")
            else:
                return get_image_file_path("settings/" + self.type + "_off.gif")
        else:
            return get_image_file_path("settings/" + self.type + ".gif")

    def render(self, draw, width, height):
        ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=self.get_image(),
            loop=False,
        ).render(draw)
