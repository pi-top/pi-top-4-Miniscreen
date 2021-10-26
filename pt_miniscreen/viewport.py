from typing import Any, Dict, List, Tuple

from PIL import Image


def calc_bounds(xy, width, height):
    """For width and height attributes, determine the bounding box if were
    positioned at ``(x, y)``."""
    left, top = xy
    right, bottom = left + width, top + height
    return [left, top, right, bottom]


def range_overlap(a_min, a_max, b_min, b_max):
    """Neither range is completely greater than the other."""
    return (a_min < b_max) and (b_min < a_max)


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
        self.mode = mode
        self.width = display_size[0]
        self.height = display_size[1]
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.size = (self.width, self.height)
        self.bounding_box = (0, 0, self.width - 1, self.height - 1)
        self.persist = False

        self._backing_image = Image.new(self.mode, self.size)
        self._position = (0, 0)
        self._hotspots: Dict[Any, List[Tuple]] = dict()

    def clear(self):
        """Initializes the device memory with an empty (blank) image."""
        self._backing_image = Image.new(self.mode, self.size)

    def set_position(self, xy):
        self._position = xy

    def add_hotspot(self, hotspot, xy, collection_id=None):
        """Add the hotspot at ``(x, y)``.

        The hotspot must fit inside the bounds of the virtual device. If
        it does not then an ``AssertError`` is raised.
        """
        (x, y) = xy
        assert 0 <= x <= self.width - hotspot.width
        assert 0 <= y <= self.height - hotspot.height

        # TODO: should it check to see whether hotspots overlap each other?
        # Is sensible to _allow_ them to overlap?
        current_collection = self._hotspots.get(collection_id, list())
        current_collection.append((hotspot, xy))
        self._hotspots[collection_id] = current_collection

    def remove_hotspot(self, hotspot, xy):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        hotspot_instance = [(hotspot, xy)]

        for collection_id, collection in self._hotspots:
            if hotspot_instance in collection:
                self._hotspots[collection_id].remove(hotspot_instance)
                if len(self._hotspots[collection_id]) == 0:
                    self._hotspot.remove(collection_id)

        eraser = Image.new(self.mode, hotspot.size)
        self._backing_image.paste(eraser, xy)

    def is_overlapping_viewport(self, hotspot, xy):
        """Checks to see if the hotspot at position ``(x, y)`` is (at least
        partially) visible according to the position of the viewport."""
        l1, t1, r1, b1 = calc_bounds(xy, hotspot.width, hotspot.height)
        l2, t2, r2, b2 = calc_bounds(
            self._position, self.window_width, self.window_height
        )
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    @property
    def image(self):
        collections_to_redraw: List[Tuple] = list()
        for collection_id, hotspot_collection in self._hotspots.items():
            for hotspot, xy in hotspot_collection:
                if not hotspot.should_redraw():
                    continue

                if not self.is_overlapping_viewport(hotspot, xy):
                    continue

                collections_to_redraw.append(hotspot_collection)

        if len(collections_to_redraw) > 0:
            for hotspot_collection in collections_to_redraw:
                for hotspot, xy in hotspot_collection:
                    self._backing_image.paste(Image.new("1", hotspot.size), xy)

                for hotspot, xy in hotspot_collection:
                    hotspot.paste_into(self._backing_image, xy)

        return self._backing_image.crop(box=self._crop_box())

    def _crop_box(self):
        (left, top) = self._position
        right = left + self.window_width
        bottom = top + self.window_height

        assert 0 <= left <= right <= self.width
        assert 0 <= top <= bottom <= self.height

        return (left, top, right, bottom)
