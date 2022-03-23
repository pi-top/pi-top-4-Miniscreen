import logging

from pt_miniscreen.hotspots.menu_page import MenuPage
from pt_miniscreen.pages.network.ap import APPage
from pt_miniscreen.pages.network.ethernet import EthernetPage
from pt_miniscreen.pages.network.usb import USBPage
from pt_miniscreen.pages.network.wifi import WifiPage
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class NetworkMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="Network",
            image_path=get_image_file_path("menu/network.gif"),
            Pages=[WifiPage, EthernetPage, APPage, USBPage]
        )
