from ..pages.settings_connection import (
    APActionPage,
    FurtherLinkActionPage,
    SSHActionPage,
    VNCActionPage,
)
from .templates import MenuTile


class SettingsConnectionMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
            pages=[
                Page(size)
                for Page in [
                    APActionPage,
                    FurtherLinkActionPage,
                    SSHActionPage,
                    VNCActionPage,
                ]
            ],
            name="Connection",
        )
