from ..pages.settings import (
    APActionPage,
    FurtherLinkActionPage,
    HDMIResetPage,
    SSHActionPage,
    VNCActionPage,
)
from .base import Menu


class SettingsMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size=size,
            pages=[
                Page(size)
                for Page in (
                    SSHActionPage,
                    VNCActionPage,
                    FurtherLinkActionPage,
                    APActionPage,
                    HDMIResetPage,
                )
            ],
            name="settings",
        )
