from enum import Enum, auto

from ...menu_base import MenuBase

default_margin_x = 29
# default_margin_y = 3
# right_text_default_margin = 10

common_first_line_y = 16
common_second_line_y = common_first_line_y + 16
common_third_line_y = common_second_line_y + 16


class Page(Enum):
    BATTERY = auto()
    CPU = auto()
    WIFI = auto()
    ETHERNET = auto()
    AP = auto()
    USB = auto()


class Menu(MenuBase):
    def __init__(self, size, mode, redraw_speed, config):
        super().__init__(size, mode, redraw_speed, config=config)
