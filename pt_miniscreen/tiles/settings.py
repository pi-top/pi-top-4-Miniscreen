from .templates import MenuTile


class SettingsMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        pages = []
        super().__init__(size, pos, pages)
