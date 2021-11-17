import logging

from .hotspot_manager import HotspotManager

logger = logging.getLogger(__name__)


class Viewport(HotspotManager):
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
        self._window_size = window_size
        self.mode = mode

        self._position = (0, 0)
        super().__init__(
            viewport_size=lambda: self.size,
            window_size=lambda: self.window_size,
            window_position=lambda: self.position,
        )

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, xy):
        self._position = xy

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, xy):
        self._window_size = xy

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
        self.register(hotspot_instance, collection_id)

    def remove_hotspot(self, hotspot_instance):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        self.unregister(hotspot_instance)

    def remove_all_hotspots(self):
        self._hotspot_collections = {}
