import logging

from pt_miniscreen.hotspots.menu_page import MenuPage
from pt_miniscreen.pages.settings.ap_toggle import APTogglePage
from pt_miniscreen.pages.settings.display_reset import DisplayResetPage
from pt_miniscreen.pages.settings.further_link_toggle import FurtherLinkTogglePage
from pt_miniscreen.pages.settings.ssh_toggle import SSHTogglePage
from pt_miniscreen.pages.settings.vnc_toggle import VNCTogglePage
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class SettingsMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="Settings",
            image_path=get_image_file_path("menu/settings.gif"),
            Pages=[
                SSHTogglePage,
                VNCTogglePage,
                FurtherLinkTogglePage,
                APTogglePage,
                DisplayResetPage,
            ],
        )
