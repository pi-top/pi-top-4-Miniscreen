from ..pages.hud import APPage, BatteryPage, CPUPage, EthernetPage, USBPage, WifiPage
from .templates import MenuTile


class HUDMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        pages = [
            Page(size)
            for Page in [
                BatteryPage,
                CPUPage,
                WifiPage,
                APPage,
                EthernetPage,
                USBPage,
            ]
        ]
        super().__init__(size, pos, pages)
