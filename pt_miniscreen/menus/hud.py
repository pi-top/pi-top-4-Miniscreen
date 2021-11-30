import logging

from ..pages.hud import APPage, BatteryPage, CPUPage, EthernetPage, USBPage, WifiPage
from .base import Menu

logger = logging.getLogger(__name__)


class HUDMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size,
            pages=[
                Page(size)
                for Page in (
                    BatteryPage,
                    CPUPage,
                    WifiPage,
                    APPage,
                    EthernetPage,
                    USBPage,
                )
            ],
            name="hud",
        )
