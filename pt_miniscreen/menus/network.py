import logging

from pt_miniscreen.core.hotspots import PaginatedHotspot
from pt_miniscreen.pages.network.ap import APPage
from pt_miniscreen.pages.network.ethernet import EthernetPage
from pt_miniscreen.pages.network.usb import USBPage
from pt_miniscreen.pages.network.wifi import WifiPage

logger = logging.getLogger(__name__)


class NetworkMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, Pages=[WifiPage, EthernetPage, APPage, USBPage])
