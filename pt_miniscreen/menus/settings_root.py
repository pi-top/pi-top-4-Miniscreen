from ..pages.settings import ConnectionPage, HDMIResetPage
from .base import Menu


class SettingsRootMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size=size,
            pages=[Page(size) for Page in [ConnectionPage, HDMIResetPage]],
            name="settings",
        )
