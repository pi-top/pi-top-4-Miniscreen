from ...pages.settings import (
    APActionPage,
    FurtherLinkActionPage,
    HDMIResetPage,
    SSHActionPage,
    VNCActionPage,
)
from ..templates import MenuTile


class SettingsMenuTile(MenuTile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(
            size=size,
            pos=pos,
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
        )
