import logging

from ..tiles import HUDMenuTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class HUDTileGroup(TileGroup):
    def __init__(
        self,
        size,
    ):
        super().__init__(size, HUDMenuTile(size=size))

    def handle_select_btn(self):
        return False

    def handle_cancel_btn(self):
        return False
