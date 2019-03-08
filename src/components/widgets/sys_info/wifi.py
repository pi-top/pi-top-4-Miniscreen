from ptcommon.sys_info import get_network_id, get_internal_ip, get_ssh_enabled_state
from components.widgets.common_functions import title_text, draw_text
from components.widgets.common_values import default_margin_x, default_margin_y
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        title_text(draw, default_margin_y, width, text="Wi-Fi Info")
        draw_text(draw, xy=(default_margin_x, height / common_first_line_y), text=str("SSID: " + get_network_id()))
        draw_text(draw, xy=(default_margin_x, height / common_second_line_y), text=str("IP: " + get_internal_ip()))
        draw_text(
            draw, xy=(default_margin_x, height / common_third_line_y), text=str("SSH: " + get_ssh_enabled_state())
        )
