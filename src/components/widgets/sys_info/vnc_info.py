from ptcommon.sys_info import get_internal_ip
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot
from getpass import getuser


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        margin = 3
        title_text(draw, margin, width, text="VNC Info")
        draw_text(draw, x=margin, y=20, text=str("  IP: " + get_internal_ip()))
        draw_text(draw, x=margin, y=35, text=str("Username: " + getuser()))
        draw_text(draw, x=margin, y=50, text=str("Password: pi-top"))
