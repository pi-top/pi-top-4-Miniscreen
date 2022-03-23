import logging

from pt_miniscreen.core.hotspots import PaginatedHotspot
from pt_miniscreen.pages.hud.network_menu_cover import NetworkMenuCoverHotspot
from pt_miniscreen.pages.hud.overview import OverviewPageHotspot
from pt_miniscreen.pages.hud.settings_menu_cover import SettingsMenuCoverHotspot
from pt_miniscreen.pages.hud.system_menu_cover import SystemMenuCoverHotspot

logger = logging.getLogger(__name__)


class HUDMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            Pages=[
                OverviewPageHotspot,
                SystemMenuCoverHotspot,
                NetworkMenuCoverHotspot,
                SettingsMenuCoverHotspot,
            ],
        )
