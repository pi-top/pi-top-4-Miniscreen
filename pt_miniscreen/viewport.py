import logging
from typing import Any, Dict, List, Tuple

from PIL import Image

logger = logging.getLogger(__name__)


class HotspotManager:
    def __init__(self) -> None:
        self._hotspot_collections: Dict[Any, List[Tuple]] = dict()

    def get_image(self, window_size, position):
        image = Image.new("1", window_size)
        for _, hotspot_collection in self._hotspot_collections.items():
            for hotspot_instance in hotspot_collection:
                if not self.is_hotspot_overlapping(
                    hotspot_instance, position, window_size
                ):
                    continue
                hotspot_instance.hotspot.paste_into(image, hotspot_instance.xy)
        return image

    def register(self, hotspot_instance, collection_id=None):
        current_collection = self._hotspot_collections.get(collection_id, list())
        current_collection.append((hotspot_instance))
        self._hotspot_collections[collection_id] = current_collection

    def unregister(self, hotspot_instance):
        for collection_id, collection in self._hotspot_collections:
            if hotspot_instance in collection:
                self._hotspot_collections[collection_id].remove(hotspot_instance)
                if len(self._hotspot_collections[collection_id]) == 0:
                    self._hotspot.remove(collection_id)

    def is_hotspot_overlapping(self, hotspot_instance, position, window_size):
        def calc_bounds(xy, width, height):
            """For width and height attributes, determine the bounding box if
            were positioned at ``(x, y)``."""
            left, top = xy
            right, bottom = left + width, top + height
            return [left, top, right, bottom]

        def range_overlap(a_min, a_max, b_min, b_max):
            """Neither range is completely greater than the other."""
            return (a_min < b_max) and (b_min < a_max)

        l1, t1, r1, b1 = calc_bounds(
            hotspot_instance.xy,
            hotspot_instance.hotspot.width,
            hotspot_instance.hotspot.height,
        )
        l2, t2, r2, b2 = calc_bounds(position, window_size[0], window_size[1])
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)


class Viewport:
    """The viewport offers a positionable window into a larger resolution
    pseudo-display, that also supports the concept of hotspots (which act like
    live displays).

    :param width: The number of horizontal pixels.
    :type width: int
    :param height: The number of vertical pixels.
    :type height: int
    :param mode: The supported color model, one of ``"1"``, ``"RGB"`` or
        ``"RGBA"`` only.
    :type mode: str
    """

    def __init__(self, display_size, window_size, mode):
        self._size = display_size
        self.window_size = window_size
        self.mode = mode

        self._position = (0, 0)
        self.hotspot_manager = HotspotManager()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def bounding_box(self):
        return (0, 0, self.width - 1, self.height - 1)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def window_width(self):
        return self.window_size[0]

    @property
    def window_height(self):
        return self.window_size[1]

    def add_hotspot(self, hotspot_instance, collection_id=None):
        """Add the hotspot at ``(x, y)``.

        The hotspot must fit inside the bounds of the virtual device. If
        it does not then an ``AssertError`` is raised.
        """
        (x, y) = hotspot_instance.xy
        assert 0 <= x <= self.width - hotspot_instance.hotspot.width
        assert 0 <= y <= self.height - hotspot_instance.hotspot.height
        self.hotspot_manager.register(hotspot_instance, collection_id)

    def remove_hotspot(self, hotspot_instance):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        self.hotspot_manager.unregister(hotspot_instance)

    @property
    def image(self):
        return self.hotspot_manager.get_image(self.window_size, self._position)

    def set_position(self, xy):
        self._position = xy
