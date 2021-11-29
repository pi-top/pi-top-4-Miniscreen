from ..pages.settings import ConnectionPage, DisplayPage
from .base import Menu


class SettingsRootMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size=size,
            pages=[Page(size) for Page in [ConnectionPage, DisplayPage]],
            name="settings",
        )
