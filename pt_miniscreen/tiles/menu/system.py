from ...pages.system import (
    BatteryPage,
    CPUPage,
    HardwarePage,
    LoginPage,
    MemoryPage,
    SoftwarePage,
)
from ..templates import MenuTile


class SystemMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
            pages=[
                SoftwarePage,
                HardwarePage,
                LoginPage,
                BatteryPage,
                CPUPage,
                MemoryPage,
            ],
        )
