import logging

from pt_miniscreen.core.hotspots import PaginatedHotspot
from pt_miniscreen.pages.settings.ap import APActionPage
from pt_miniscreen.pages.settings.further_link import FurtherLinkActionPage
from pt_miniscreen.pages.settings.hdmi_reset import HDMIResetPage
from pt_miniscreen.pages.settings.ssh import SSHActionPage
from pt_miniscreen.pages.settings.vnc import VNCActionPage

logger = logging.getLogger(__name__)


class SettingsMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            Pages=[
                SSHActionPage,
                VNCActionPage,
                FurtherLinkActionPage,
                APActionPage,
                HDMIResetPage,
            ]
        )
