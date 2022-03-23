import logging

from pt_miniscreen.core.hotspots import PaginatedHotspot
from pt_miniscreen.pages.system.battery import BatteryPage
from pt_miniscreen.pages.system.cpu import CPUPage
from pt_miniscreen.pages.system.login import LoginDetailsPage
from pt_miniscreen.pages.system.memory import MemoryPage

logger = logging.getLogger(__name__)


class SystemMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            Pages=[
                LoginDetailsPage,
                BatteryPage,
                CPUPage,
                MemoryPage,
            ]
        )
