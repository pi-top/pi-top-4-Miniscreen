from ptcommon.sys_info import get_battery_capacity, get_battery_charging_state
from components.widgets.common_functions import draw_text
from components.widgets.common_values import default_margin_x, common_first_line_y, common_second_line_y
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

    def render(self, draw, width, height):
        draw_text(draw, xy=(default_margin_x, common_first_line_y), text="Capacity: " + get_battery_capacity())
        draw_text(draw, xy=(default_margin_x, common_second_line_y), text=get_battery_charging_state())
