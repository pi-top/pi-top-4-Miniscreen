from ...pages.network import APPage, EthernetPage, USBPage, WifiPage
from ..templates import MenuTile


class NetworkMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
            pages=[
                WifiPage,
                EthernetPage,
                APPage,
                USBPage,
            ],
        )
