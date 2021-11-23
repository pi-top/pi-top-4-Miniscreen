from ..pages.hud.battery import Page as BatteryPage
from .templates import MenuTile


class HUDMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        pages = [BatteryPage(size)]
        super().__init__(size, pos, pages)
