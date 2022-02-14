import logging

from ..pages.system import BatteryPage, CPUPage
from .base import Menu

logger = logging.getLogger(__name__)


class SystemMenu(Menu):
    def __init__(self, size):
        super().__init__(
            size,
            pages=[
                Page(size)
                for Page in (
                    BatteryPage,
                    CPUPage,
                )
            ],
            name="system",
        )
