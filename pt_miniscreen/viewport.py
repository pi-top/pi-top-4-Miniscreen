import logging
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageOps
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

logger = logging.getLogger(__name__)


class HotspotManager:
    def __init__(self, viewport_size, window_size, window_position) -> None:
        self._hotspot_collections: Dict[Any, List[Tuple]] = dict()
        self._viewport_size_func = viewport_size
        self._window_size_func = window_size
        self._window_position_func = window_position
        self.cached_images: Dict = dict()

    @property
    def viewport_size(self):
        if callable(self._viewport_size_func):
            return self._viewport_size_func()
        return self._viewport_size_func

    @property
    def window_size(self):
        if callable(self._window_size_func):
            return self._window_size_func()
        return self._window_size_func

    @property
    def window_position(self):
        if callable(self._window_position_func):
            return self._window_position_func()
        return self._window_position_func

    def _crop_box(self):
        (left, top) = self.window_position
        right = left + self.window_size[0]
        bottom = top + self.window_size[1]

        assert 0 <= left <= right <= self.viewport_size[0]
        assert 0 <= top <= bottom <= self.viewport_size[1]

        return (left, top, right, bottom)

    def paste_hotspot_into_image(self, hotspot_instance, image):
        if (
            not hotspot_instance.hotspot.draw_white
            and not hotspot_instance.hotspot.draw_black
        ):
            return

        hotspot_image = self.cached_images.get(hotspot_instance.hotspot)
        if not hotspot_image:
            return

        if hotspot_instance.hotspot.invert:
            hotspot_image = MiniscreenAssistant(
                hotspot_instance.hotspot.mode, hotspot_instance.hotspot.size
            ).invert(hotspot_image)

        mask = None
        if (
            hotspot_instance.hotspot.draw_white
            and not hotspot_instance.hotspot.draw_black
        ):
            mask = hotspot_image

        elif (
            not hotspot_instance.hotspot.draw_white
            and hotspot_instance.hotspot.draw_black
        ):
            mask = ImageOps.invert(hotspot_image)

        pos = hotspot_instance.xy
        # box = pos + (pos[0] + hotspot_image.size[0], pos[1] + hotspot_image.size[1])
        logger.debug(f"hotspot xy: {hotspot_instance.xy}")
        logger.debug(f"position: {pos}")
        # logger.debug(f"box: {box}")
        logger.debug(hotspot_image.size)
        image.paste(hotspot_image, pos, mask)

    def get_image(self):
        from pprint import pformat

        image = Image.new("1", self.viewport_size)
        updated_hotspots = list()
        for _, hotspot_collection in self._hotspot_collections.items():
            for hotspot_instance in hotspot_collection:
                if not self.is_hotspot_overlapping(hotspot_instance):
                    continue

                self.paste_hotspot_into_image(hotspot_instance, image)
                updated_hotspots.append(hotspot_instance)

        logger.debug("Updated hotspots:")
        logger.debug(pformat(updated_hotspots))
        im = image.crop(box=self._crop_box())
        return im

    def register(self, hotspot_instance, collection_id=None):
        logger.debug(f"HotspotManager.register {hotspot_instance}")
        current_collection = self._hotspot_collections.get(collection_id, list())
        if hotspot_instance in current_collection:
            raise Exception(f"Hotspot instance {hotspot_instance} already registered")
        current_collection.append((hotspot_instance))
        self._hotspot_collections[collection_id] = current_collection
        self.cached_images[hotspot_instance.hotspot] = dict()

        from threading import Thread
        from time import sleep

        def run():
            while True:
                if self.is_hotspot_overlapping(hotspot_instance):
                    self.cached_images[
                        hotspot_instance.hotspot
                    ] = hotspot_instance.hotspot.image

                sleep(hotspot_instance.hotspot.interval)

        t = Thread(target=run, args=(), daemon=True)
        t.start()

    def unregister(self, hotspot_instance):
        for collection_id, collection in self._hotspot_collections:
            if hotspot_instance in collection:
                self._hotspot_collections[collection_id].remove(hotspot_instance)
                if len(self._hotspot_collections[collection_id]) == 0:
                    self._hotspot.remove(collection_id)

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
        l2, t2, r2, b2 = calc_bounds(
            self.window_position, self.window_size[0], self.window_size[1]
        )
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    @property
    def image(self):
        return self.get_image()


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
