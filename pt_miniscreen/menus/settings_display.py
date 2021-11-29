from ..pages.settings_display.hdmi_reset import HDMIResetPage
from .base import Menu


class SettingsDisplayMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size=size,
            pages=[HDMIResetPage(size)],
            name="display",
        )
