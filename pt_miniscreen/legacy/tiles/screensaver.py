import logging

from pt_miniscreen.hotspots.base import HotspotInstance

from ..hotspots.legacy.starfield_screensaver import (
    Hotspot as StarfieldScreensaverHotspot,
)
from .base import Tile

logger = logging.getLogger(__name__)


class StarfieldScreensaverTile(Tile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(size, pos=pos)

        hotspot_instances = list()
        hotspot_instances.append(
            HotspotInstance(StarfieldScreensaverHotspot(size), (0, 0))
        )
        self.set_hotspot_instances(hotspot_instances)
