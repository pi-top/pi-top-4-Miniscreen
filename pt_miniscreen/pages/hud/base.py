from enum import Enum, auto

from ...menu_base import MenuBase


class Page(Enum):
    BATTERY = auto()
    CPU = auto()
    WIFI = auto()
    ETHERNET = auto()
    AP = auto()
    USB = auto()


class Menu(MenuBase):
    def __init__(self, size, mode, redraw_speed, children):
        super().__init__(size, mode, redraw_speed, children=children)
