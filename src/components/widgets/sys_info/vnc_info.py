from ptcommon.sys_info import get_internal_ip
from components.widgets.common_functions import (
    right_text,
    title_text,
    draw_text,
    align_to_middle,
)
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_values import top_margin, default_margin
from getpass import getuser


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        username = "pi" if getuser() == "root" else getuser()
        title_text(draw, top_margin, width, text="VNC Info")
        draw_text(
            draw, xy=(default_margin, (height * 1 / 4)), text=str("IP: " + get_internal_ip())
        )
        draw_text(
            draw, xy=(default_margin, (height * 2 / 4)), text=str("Username: " + username)
        )
        draw_text(draw, xy=(default_margin, (height * 3 / 4)), text=str("Password: pi-top"))
