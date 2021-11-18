import logging

from PIL import Image

from .base import Tile

logger = logging.getLogger(__name__)


class ViewportTile(Tile):
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

    def __init__(self, size, mode, viewport_size, window_position=(0, 0)):
        self.mode = mode

        # TODO: move to viewport tile
        self._viewport_size = viewport_size
        self._window_position = window_position

        self._position = (0, 0)
        super().__init__(size)

    # TODO: create a base version of this function that always returns true
    # Move this to viewport
    def is_hotspot_overlapping(self, hotspot_instance):
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
        l2, t2, r2, b2 = calc_bounds(self.window_position, self.size[0], self.size[1])
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    def _crop_box(self):
        (left, top) = self.window_position
        right = left + self.size[0]
        bottom = top + self.size[1]

        assert 0 <= left <= right <= self.viewport_size[0]
        assert 0 <= top <= bottom <= self.viewport_size[1]

        return (left, top, right, bottom)

    @property
    def viewport_size(self):
        if callable(self._viewport_size):
            return self._viewport_size()

        if self._viewport_size is None:
            return self.size

        return self._viewport_size

    @property
    def window_position(self):
        if callable(self._window_position):
            return self._window_position()
        return self._window_position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, xy):
        self._position = xy

    @property
    def y_pos(self):
        return self._position[1]

    @y_pos.setter
    def y_pos(self, pos):
        self.position = (0, pos)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, xy):
        self._size = xy

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

    @height.setter
    def height(self, value):
        self.size = (self.width, value)

    def add_hotspot(self, hotspot_instance, collection_id=None):
        """Add the hotspot at ``(x, y)``.

        The hotspot must fit inside the bounds of the virtual device. If
        it does not then an ``AssertError`` is raised.
        """
        (x, y) = hotspot_instance.xy
        assert 0 <= x <= self.width - hotspot_instance.hotspot.width
        assert 0 <= y <= self.height - hotspot_instance.hotspot.height
        self.register(hotspot_instance, collection_id)

    def remove_hotspot(self, hotspot_instance):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        self.unregister(hotspot_instance)

    def get_preprocess_image(self):
        return Image.new("1", self.viewport_size)

    def process_image(self, image):
        for _, hotspot_collection in self._hotspot_collections.items():
            for hotspot_instance in hotspot_collection:
                if not self.is_hotspot_overlapping(hotspot_instance):
                    continue
                self._paste_hotspot_into_image(hotspot_instance, image)
        return image

    def post_process_image(self, image):
        return image.crop(box=self._crop_box())
