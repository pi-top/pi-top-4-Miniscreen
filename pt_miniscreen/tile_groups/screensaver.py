import logging

from ..tiles import StarfieldScreensaverTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class StarfieldScreensaverTileGroup(TileGroup):
    def __init__(
        self,
        size,
    ):
        super().__init__(size=size, menu_tile=StarfieldScreensaverTile(size=size))
