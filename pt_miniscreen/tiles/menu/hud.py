from ...menus.hud import HUDMenu
from ..templates import MenuTile


class HUDMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(menu_cls=HUDMenu, size=size, pos=pos)
