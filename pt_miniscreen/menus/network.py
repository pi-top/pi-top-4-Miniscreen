import logging

from ..pages.network import APPage, EthernetPage, USBPage, WifiPage
from .base import Menu

logger = logging.getLogger(__name__)


class NetworkMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size,
            pages=[
                Page(size)
                for Page in (
                    WifiPage,
                    EthernetPage,
                    APPage,
                    USBPage,
                )
            ],
            name="network",
        )
