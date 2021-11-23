from ..pages.hud.battery import Page as BatteryPage
from ..pages.hud.cpu import Page as CPUPage
from .templates import MenuTile


class HUDMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        pages = [BatteryPage(size), CPUPage(size)]
        super().__init__(size, pos, pages)
