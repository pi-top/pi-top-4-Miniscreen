import logging

from ..tiles import HUDMenuTile
from .base import TileGroup as TileGroupBase

logger = logging.getLogger(__name__)


class TileGroup(TileGroupBase):
    def __init__(
        self,
        size,
    ):
        super().__init__(size, HUDMenuTile(size=self.miniscreen.size))
