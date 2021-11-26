from ..pages.settings import ConnectionPage, DisplayPage
from .templates import MenuTile


class SettingsMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
            pages=[Page(size) for Page in [ConnectionPage, DisplayPage]],
        )
