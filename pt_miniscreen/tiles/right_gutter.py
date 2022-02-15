import logging

from pt_miniscreen.hotspots.base.hotspot_instance import HotspotInstance
from pt_miniscreen.tiles.base import Tile
from pt_miniscreen.utils import get_image_file_path

from ..hotspots.templates.image import Hotspot as ImageHotspot
from ..hotspots.templates.rectangle import Hotspot as RectangleHotspot

logger = logging.getLogger(__name__)


class RightGutterTile(Tile):
    def __init__(self, size, pos=(0, 0)):
        super().__init__(size=size, pos=pos)

        self.icon_size = (5, 5)
        icon_padding = (3, 7)
        self.top_icon_xy = icon_padding
        self.bottom_icon_xy = (
            icon_padding[0],
            size[1] - icon_padding[1] - self.icon_size[1],
        )

        # add hotspot attributes
        self._left_arrow = None
        self._right_arrow = None
        self._tick = None

        # add left border
        self.add_hotspot_instance(
            HotspotInstance(
                xy=(0, 0),
                hotspot=RectangleHotspot(size=(1, size[1])),
            )
        )

    def _create_left_arrow(self):
        self._left_arrow = HotspotInstance(
            xy=self.top_icon_xy,
            hotspot=ImageHotspot(
                image_path=get_image_file_path("gutter/left_arrow.png"),
                size=self.icon_size,
            ),
        )
        return self._left_arrow

    def _create_right_arrow(self):
        self._right_arrow = HotspotInstance(
            xy=self.bottom_icon_xy,
            hotspot=ImageHotspot(
                image_path=get_image_file_path("gutter/right_arrow.png"),
                size=self.icon_size,
            ),
        )
        return self._right_arrow

    def _create_tick(self):
        self._tick = HotspotInstance(
            xy=self.bottom_icon_xy,
            hotspot=ImageHotspot(
                image_path=get_image_file_path("gutter/tick.png"), size=self.icon_size
            ),
        )
        return self._tick

    def set_left_arrow_visible(self, next_is_visible):
        is_visible = self._left_arrow in self.hotspot_instances

        if next_is_visible and not is_visible:
            self.add_hotspot_instance(self._create_left_arrow())

        if not next_is_visible and is_visible:
            self.remove_hotspot_instance(self._left_arrow)

    def set_right_arrow_visible(self, next_is_visible):
        right_arrow_is_visible = self._right_arrow in self.hotspot_instances
        tick_is_visible = self._tick in self.hotspot_instances

        if next_is_visible and not right_arrow_is_visible:
            if tick_is_visible:
                self.remove_hotspot_instance(self._tick)

            self.add_hotspot_instance(self._create_right_arrow())

        if not next_is_visible and right_arrow_is_visible:
            self.remove_hotspot_instance(self._right_arrow)

    def set_tick_visible(self, next_is_visible):
        tick_is_visible = self._tick in self.hotspot_instances
        right_arrow_is_visible = self._right_arrow in self.hotspot_instances

        if next_is_visible and not tick_is_visible:
            if right_arrow_is_visible:
                self.remove_hotspot_instance(self._right_arrow)

            self.add_hotspot_instance(self._create_tick())

        if not next_is_visible and tick_is_visible:
            self.remove_hotspot_instance(self._tick)
