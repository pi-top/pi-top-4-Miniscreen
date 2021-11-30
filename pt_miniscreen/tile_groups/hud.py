import logging

from ..tiles import HUDMenuTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class HUDTileGroup(TileGroup):
    def __init__(
        self,
        size,
    ):
        super().__init__(size=size, menu_tile=HUDMenuTile(size=size))
