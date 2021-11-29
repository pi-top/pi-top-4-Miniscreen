from ...menus import SettingsRootMenu
from ..templates import MenuTile


class SettingsMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            menu_cls=SettingsRootMenu,
            size=size,
            pos=pos,
            name="settings",
        )
