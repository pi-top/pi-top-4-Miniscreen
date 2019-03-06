from ptcommon.sys_info import get_internal_ip
from components.widgets.common_functions import right_text, title_text, draw_text, align_to_middle
from components.widgets.common.base_widget_hotspot import BaseHotspot
from getpass import getuser
from ptcommon.pt_os import eula_agreed


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)


    @staticmethod
    def render(draw, width, height):
        margin = 3
        username = getuser() if eula_agreed() else "pi"
        title_text(draw, margin, width, text="VNC Info")
        draw_text(draw, xy=(margin, (height * 1 / 4)), text=str("IP: " + get_internal_ip()))
        draw_text(draw, xy=(margin, (height * 2 / 4)), text=str("Username: " + username))
        draw_text(draw, xy=(margin, (height * 3 / 4)), text=str("Password: pi-top"))
