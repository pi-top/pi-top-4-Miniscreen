from ...pages.system import BatteryPage, CPUPage
from ..templates import MenuTile


class SystemMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
            pages=[
                BatteryPage,
                CPUPage,
            ],
        )
