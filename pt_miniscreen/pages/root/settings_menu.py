import logging
import os

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.pages.settings.ap_toggle import APTogglePage
from pt_miniscreen.pages.settings.cloudflare_dns import CloudflareDnsPage
from pt_miniscreen.pages.settings.display_reset import DisplayResetPage
from pt_miniscreen.pages.settings.further_link_toggle import FurtherLinkTogglePage
from pt_miniscreen.pages.settings.guacamole_toggle import GuacamoleTogglePage
from pt_miniscreen.pages.settings.ssh_toggle import SSHTogglePage
from pt_miniscreen.pages.settings.vnc_toggle import VNCTogglePage
from pt_miniscreen.pages.settings.bluetooth_encrypted_gatt_toggle_page import (
    BluetoothEncryptedGattTogglePage,
)

from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


def _feature_enabled(env_var):
    return os.environ.get(env_var, "").strip().lower() in ("1", "true", "yes", "on")


class SettingsMenuPage(MenuPage):
    def __init__(self, **kwargs):
        pages = [
            SSHTogglePage,
            VNCTogglePage,
        ]
        if _feature_enabled("PI_MINISCREEN_FEATURE_GUACAMOLE"):
            pages.append(GuacamoleTogglePage)
        pages += [
            FurtherLinkTogglePage,
            APTogglePage,
            BluetoothEncryptedGattTogglePage,
            DisplayResetPage,
            CloudflareDnsPage,
        ]

        super().__init__(
            **kwargs,
            text="Settings",
            image_path=get_image_file_path("menu/settings.gif"),
            virtual_page_list=False,  # pages should keep state when not visible
            Pages=pages,
        )
