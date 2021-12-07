import logging

from PIL import Image

from ...types import BoundingBox, Coordinate
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

    def __init__(
        self,
        size: Coordinate,
        pos: Coordinate,
        viewport_size: Coordinate,
        window_position: Coordinate = (0, 0),
    ) -> None:
        self._viewport_size: Coordinate = viewport_size
        self._window_position: Coordinate = window_position

        super().__init__(size=size, pos=pos)

    def _crop_box(self) -> BoundingBox:
        (left, top) = self.window_position
        right = left + self.size[0]
        bottom = top + self.size[1]

        assert 0 <= left <= right <= self.viewport_size[0]
        assert 0 <= top <= bottom <= self.viewport_size[1]

        return (left, top, right, bottom)

    @property
    def viewport_size(self) -> Coordinate:
        if self._viewport_size is None:
            return self.size

        return self._viewport_size

    @viewport_size.setter
    def viewport_size(self, value: Coordinate) -> None:
        self._viewport_size = value

    def update_all_hotspot_instances(self):
        [
            i.set_active_based_on_if_visible_in_window(self.window_position, self.size)
            for i in self.hotspot_instances
        ]

    @property
    def window_position(self) -> Coordinate:
        return self._window_position

    @window_position.setter
    def window_position(self, position: Coordinate) -> None:
        self._window_position = position
        self.update_all_hotspot_instances()

    @property
    def y_pos(self) -> int:
        return self.window_position[1]

    @y_pos.setter
    def y_pos(self, pos: int) -> None:
        self.window_position = (self.window_position[0], pos)

    def get_preprocess_image(self) -> Image.Image:
        return Image.new("1", self.viewport_size)

    def post_process_image(self, image: Image.Image) -> Image.Image:
        return image.crop(box=self._crop_box())
