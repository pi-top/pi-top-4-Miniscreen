import logging

from ..pages.hud import NetworkMenuPage, OverviewPage, SettingsMenuPage, SystemMenuPage
from .base import Menu

logger = logging.getLogger(__name__)


class HUDMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size,
            pages=[
                Page(size)
                for Page in (
                    OverviewPage,
                    SystemMenuPage,
                    NetworkMenuPage,
                    SettingsMenuPage,
                )
            ],
            name="hud",
        )
