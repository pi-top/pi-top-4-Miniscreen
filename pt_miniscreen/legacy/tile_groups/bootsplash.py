import logging

from ..tiles import PitopBootsplashTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class PitopBootsplashTileGroup(TileGroup):
    def __init__(
        self,
        size,
    ):
        super().__init__(size=size, menu_tile=PitopBootsplashTile(size=size))
