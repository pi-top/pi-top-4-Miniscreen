import logging
import time
from typing import List

from PIL import Image

from ..hotspots.base import HotspotInstance
from ..types import BoundingBox, Coordinate

logger = logging.getLogger(__name__)


class Tile:
    def __init__(self, size: Coordinate, pos: Coordinate = (0, 0)) -> None:
        self._size: Coordinate = size
        self.pos: Coordinate = pos
        self.active: bool = False
        self.hotspot_instances: List[HotspotInstance] = list()
        self._render_size: Coordinate = self.size

    def reset(self) -> None:
        pass

    @property
    def window_position(self) -> Coordinate:
        return (0, 0)

    @property
    def size(self) -> Coordinate:
        return self._size

    @size.setter
    def size(self, xy: Coordinate):
        if xy == self.size:
            return

        self._size = xy
        self.reset()

    @property
    def bounding_box(self) -> BoundingBox:
        return (0, 0, self.width - 1, self.height - 1)

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    @height.setter
    def height(self, value: int) -> None:
        self.size = (self.width, value)

    @property
    def render_size(self) -> Coordinate:
        return (
            self._render_size
            if self._render_size[0] > self.size[0]
            or self._render_size[1] > self.size[1]
            else self.size
        )

    def set_hotspot_instances(self, hotspot_instances: List[HotspotInstance]) -> None:
        self.remove_all_hotspot_instances()
        logger.debug(f"Adding {len(hotspot_instances)} hotspot instances...")
        for hotspot_instance in hotspot_instances:
            self.add_hotspot_instance(hotspot_instance)

    def add_hotspot_instance(self, hotspot_instance: HotspotInstance) -> None:
        (x, y) = hotspot_instance.xy

        # xy + size = max size needed to render a given hotspot instance
        # self._render_size manages this max size for all added hotspot instances
        max_x = x + hotspot_instance.size[0]
        if max_x > self.render_size[0]:
            self._render_size = (max_x, self.render_size[1])

        max_y = y + hotspot_instance.size[1]
        if max_y > self.render_size[1]:
            self._render_size = (self.render_size[0], max_y)

        if hotspot_instance in self.hotspot_instances:
            raise Exception(f"Hotspot instance {hotspot_instance} already registered")

        self.hotspot_instances.append((hotspot_instance))
        hotspot_instance.set_active_based_on_if_visible_in_window(
            self.window_position, self.size
        )

    def remove_hotspot_instance(self, hotspot_instance: HotspotInstance):
        self.hotspot_instances.remove(hotspot_instance)

    def remove_all_hotspot_instances(self) -> None:
        if len(self.hotspot_instances) == 0:
            return

        logger.debug(f"Removing {len(self.hotspot_instances)} hotspot instances...")
        self.hotspot_instances = list()

    def get_preprocess_image(self) -> Image.Image:
        return Image.new("1", self.render_size)

    def process_image(self, image: Image.Image) -> Image.Image:
        [
            i.paste_into_image_if_visible_in_window(
                image, self.window_position, self.size
            )
            for i in self.hotspot_instances
        ]

        return image

    def post_process_image(self, image: Image.Image) -> Image.Image:
        return image if image.size == self.size else image.crop(box=(0, 0) + self.size)

    @property
    def image(self) -> Image.Image:
        im = self.get_preprocess_image()

        if not self.active:
            logger.debug("Tile is not active - returning unprocessed image")
            return im

        start = time.time()

        im = self.post_process_image(self.process_image(im))

        end = time.time()
        logger.debug(f"Time generating tile image: {end - start}")

        return im

    def handle_select_btn(self) -> bool:
        return False

    def handle_cancel_btn(self) -> bool:
        return False

    def handle_up_btn(self) -> bool:
        return self.needs_to_scroll

    def handle_down_btn(self) -> bool:
        return self.needs_to_scroll

    @property
    def needs_to_scroll(self) -> bool:
        return False
