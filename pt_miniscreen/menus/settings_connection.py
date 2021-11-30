from ..pages.settings_connection import (
    APActionPage,
    FurtherLinkActionPage,
    SSHActionPage,
    VNCActionPage,
)
from .base import Menu


class SettingsConnectionMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size=size,
            pages=[
                Page(size)
                for Page in [
                    SSHActionPage,
                    VNCActionPage,
                    FurtherLinkActionPage,
                    APActionPage,
                ]
            ],
            name="connection",
        )
