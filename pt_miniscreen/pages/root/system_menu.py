import logging

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.pages.system.battery import BatteryPage
from pt_miniscreen.pages.system.cpu import CPUPage
from pt_miniscreen.pages.system.login import LoginDetailsPage
from pt_miniscreen.pages.system.memory import MemoryPage
from pt_miniscreen.pages.system.pt_hardware import PitopHardwarePage
from pt_miniscreen.pages.system.rpi_hardware import RPiHardwarePage
from pt_miniscreen.pages.system.software import SoftwarePage
from pt_miniscreen.pages.system.last_update import LastUpdatePage
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class SystemMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="System",
            image_path=get_image_file_path("menu/system.gif"),
            image_size=(29, 29),
            Pages=[
                LoginDetailsPage,
                BatteryPage,
                CPUPage,
                MemoryPage,
                LastUpdatePage,
                SoftwarePage,
                PitopHardwarePage,
                RPiHardwarePage,
            ]
        )
