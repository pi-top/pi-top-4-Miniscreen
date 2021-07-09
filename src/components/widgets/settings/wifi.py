from components.widgets.common.functions import get_image_file_path
from components.widgets.common.base_widgets import BaseHotspot
from components.widgets.common.image_component import ImageComponent
from components.helpers.menu_page_actions import WifiModes


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
            wifi_mode = self.get_state_method()
            if wifi_mode == WifiModes.STA:
                return get_image_file_path("settings/" + self.type + "_off.png")
            elif wifi_mode == WifiModes.AP_STA:
                return get_image_file_path("settings/" + self.type + "_on.png")

    def render(self, draw, width, height):
        ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=self.get_image(),
            loop=False,
        ).render(draw)
