import logging
from threading import Thread
from time import sleep
from typing import Any, Dict, List, Tuple

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .event import AppEvents, post_event

logger = logging.getLogger(__name__)


class HotspotManager:
    def __init__(self, viewport_size, window_size, window_position) -> None:
        self._hotspot_collections: Dict[Any, List[Tuple]] = dict()
        self._viewport_size_func = viewport_size
        self._window_size_func = window_size
        self._window_position_func = window_position
        self.cached_images: Dict = dict()
        self.image_caching_threads: Dict = dict()
        self.update_cached_images = False
        self.active = False

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

        if not self.update_cached_images:
            logger.debug(
                "paste_hotspot_into_image - Not caching images anymore - returning"
            )
            return

        hotspot_image = self.cached_images.get(hotspot_instance.hotspot)
        if not hotspot_image:
            return

        if hotspot_instance.hotspot.invert:
            hotspot_image = MiniscreenAssistant(
                hotspot_instance.hotspot.mode, hotspot_instance.hotspot.size
            ).invert(hotspot_image)

        mask = hotspot_instance.hotspot.mask(hotspot_image)
        pos = hotspot_instance.xy
        # box = pos + (pos[0] + hotspot_image.size[0], pos[1] + hotspot_image.size[1])
        logger.debug(
            f"viewport.paste_hotspot_into_image - hotspot image size: {hotspot_image.size}"
        )
        logger.debug(
            f"viewport.paste_hotspot_into_image - base image size: {image.size}"
        )
        logger.debug(
            f"viewport.paste_hotspot_into_image - hotspot xy: {hotspot_instance.xy}"
        )
        logger.debug(f"viewport.paste_hotspot_into_image - position: {pos}")
        image.paste(hotspot_image, pos, mask)

    def get_image(self):
        from pprint import pformat

        if not self.update_cached_images:
            logger.debug("Not caching images anymore - returning")
            return

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

        self._register_thread(hotspot_instance)

    def _register_thread(self, hotspot_instance):
        def run():
            while self.update_cached_images:
                if self.is_hotspot_overlapping(hotspot_instance):
                    self.cached_images[
                        hotspot_instance.hotspot
                    ] = hotspot_instance.hotspot.image
                    if self.active:
                        post_event(AppEvents.REDRAWN_HOTSPOT, self)

                sleep(hotspot_instance.hotspot.interval)

        self.update_cached_images = True
        thread = Thread(target=run, args=(), daemon=True)
        thread.name = hotspot_instance.hotspot
        thread.start()
        self.image_caching_threads[hotspot_instance.hotspot] = thread

    def stop_threads(self):
        self.update_cached_images = False
        for hotspot, thread in self.image_caching_threads.items():
            thread.join(0)
        logger.debug("stop_threads - stopped all threads")

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

    def remove_all_hotspots(self):
        self._hotspot_collections = {}
