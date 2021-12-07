import logging

from ..hotspots.base import HotspotInstance
from ..hotspots.bootsplash_hotspot import BootsplashHotspot
from .base import Tile

logger = logging.getLogger(__name__)


class PitopBootsplashTile(Tile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(size=size, pos=pos)

        hotspot_instances = list()
        hotspot_instances.append(HotspotInstance(BootsplashHotspot(size), (0, 0)))
        self.set_hotspot_instances(hotspot_instances)
