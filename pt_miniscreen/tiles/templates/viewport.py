import logging

from PIL import Image

from ..base import Tile

logger = logging.getLogger(__name__)


class ViewportTile(Tile):
    """The viewport offers a positionable window into a larger resolution
    pseudo-display, that also supports the concept of hotspots (which act like
    live displays).

    :param width: The number of horizontal pixels.
    :type width: int
    :param height: The number of vertical pixels.
    :type height: int
    """

    def __init__(self, size, pos, viewport_size, window_position=(0, 0)):
        self._viewport_size = viewport_size
        self._window_position = window_position

        super().__init__(size=size, pos=pos)

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

    @viewport_size.setter
    def viewport_size(self, value):
        self._viewport_size = value

    @property
    def window_position(self):
        if callable(self._window_position):
            return self._window_position()
        return self._window_position

    @window_position.setter
    def window_position(self, position):
        self._window_position = position

    @property
    def y_pos(self):
        return self.window_position[1]

    @y_pos.setter
    def y_pos(self, pos):
        self.window_position = (self.window_position[0], pos)

    def get_preprocess_image(self):
        return Image.new("1", self.viewport_size)

    def process_image(self, image):
        for hotspot_instance in self.hotspot_instances:
            if not self.is_hotspot_overlapping(hotspot_instance):
                continue
            self._paste_hotspot_into_image(hotspot_instance, image)
        return image

    def post_process_image(self, image):
        return image.crop(box=self._crop_box())
