from ...pages.system import (
    BatteryPage,
    CPUPage,
    LoginPage,
    MemoryPage,
    PitopHardwarePage,
    RPiHardwarePage,
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
                PitopHardwarePage,
                RPiHardwarePage,
                LoginPage,
                BatteryPage,
                CPUPage,
                MemoryPage,
            ],
        )
