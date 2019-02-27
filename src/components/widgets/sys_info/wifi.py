from ptcommon.sys_info import get_network_id, get_internal_ip, get_ssh_enabled_state
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        margin = 3
        title_text(draw, margin, width, text="Wi-Fi Info")
        draw_text(draw, x=margin, y=20, text=str("SSID: " + get_network_id()))
        draw_text(draw, x=margin, y=35, text=str("  IP: " + get_internal_ip()))
        draw_text(draw, x=margin, y=50, text=str(" SSH: " + get_ssh_enabled_state()))
