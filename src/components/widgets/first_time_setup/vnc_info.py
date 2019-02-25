from ptcommon.sys_info import get_internal_ip
from components.widgets.common_functions import right_text, title_text, tiny_font
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        margin = 3
        title_text(draw, margin, width, text="VNC Info")
        draw.text(
            (margin, 20),
            text=str("  IP: " + get_internal_ip()),
            font=tiny_font,
            fill="white",
        )
        draw.text(
            (margin, 35),
            text=str("Username: pi"),
            font=tiny_font,
            fill="white",
        )
        draw.text(
            (margin, 50),
            text=str("Password: pi-top"),
            font=tiny_font,
            fill="white",
        )
