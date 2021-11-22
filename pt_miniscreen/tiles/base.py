import logging
import time
from threading import Thread
from time import sleep
from typing import Any, Dict, List, Tuple

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..event import AppEvents, post_event
from ..hotspots.base import HotspotInstance

logger = logging.getLogger(__name__)


class Tile:
    def __init__(self, size=None) -> None:
        self._hotspot_collections: Dict[Any, List[Tuple]] = dict()
        self._size = size
        self.cached_images: Dict = dict()
        self.image_caching_threads: Dict = dict()
        self.update_cached_images = True
        self.active = False

    def _add_hotspots_into_(self):
        self.remove_all_hotspots()
        for i, collection in enumerate(self._hotspot_collections):
            # for upperleft_xy, hotspots in collection.hotspots.items():
            for upperleft_xy, hotspots in self._hotspot_collection.items():
                for hotspot in hotspots:
                    pos = (
                        int(upperleft_xy[0]),
                        int(upperleft_xy[1] + i * self.height),
                    )
                    self.add_hotspot(
                        HotspotInstance(hotspot, pos), collection_id=collection
                    )

    @property
    def size(self):
        if callable(self._size):
            return self._size()

        return self._size

    @size.setter
    def size(self, xy):
        self._size = xy

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

    def _paste_hotspot_into_image(self, hotspot_instance, image):
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

    def register(self, hotspot_instance, collection_id=None):
        (x, y) = hotspot_instance.xy
        assert 0 <= x <= self.width - hotspot_instance.hotspot.width
        assert 0 <= y <= self.height - hotspot_instance.hotspot.height

        logger.debug(f"Tile.register {hotspot_instance}")
        current_collection = self._hotspot_collections.get(collection_id, list())
        if hotspot_instance in current_collection:
            raise Exception(f"Hotspot instance {hotspot_instance} already registered")
        current_collection.append((hotspot_instance))
        self._hotspot_collections[collection_id] = current_collection
        self.cached_images[hotspot_instance.hotspot] = dict()

        self._register_thread(hotspot_instance)

    def unregister(self, hotspot_instance):
        for collection_id, collection in self._hotspot_collections:
            if hotspot_instance in collection:
                self._hotspot_collections[collection_id].remove(hotspot_instance)
                if len(self._hotspot_collections[collection_id]) == 0:
                    self._hotspot.remove(collection_id)

    def _register_thread(self, hotspot_instance):
        hotspot = hotspot_instance.hotspot

        def run():
            def cache_new_image():
                self.cached_images[hotspot] = hotspot.image

            cache_new_image()
            while self.update_cached_images:
                # TODO: improve this "busy wait"
                # if not active, there's no need to check - perhaps instead of sleeping,
                # we should wait on an event triggered on active state change?
                #
                # another thing to consider would be to do something similar with 'is overlapping'
                # - if we are not overlapping, and the position is not changing, then this is still
                # busy waiting...
                if self.active and self.is_hotspot_overlapping(hotspot_instance):
                    cache_new_image()
                    post_event(AppEvents.ACTIVE_HOTSPOT_HAS_NEW_CACHED_IMAGE)
                sleep(hotspot.interval)

        thread = Thread(target=run, args=(), daemon=True, name=hotspot)
        thread.start()
        self.image_caching_threads[hotspot] = thread

    def stop_threads(self):
        self.update_cached_images = False
        for hotspot, thread in self.image_caching_threads.items():
            thread.join(0)
        logger.debug("stop_threads - stopped all threads")

    def remove_all_hotspots(self):
        self._hotspot_collections = {}

    def is_hotspot_overlapping(self, hotspot_instance):
        return True

    def get_preprocess_image(self):
        return Image.new("1", self.size)

    def process_image(self, image):
        for _, hotspot_collection in self._hotspot_collections.items():
            for hotspot_instance in hotspot_collection:
                if not self.is_hotspot_overlapping(hotspot_instance):
                    continue
                self._paste_hotspot_into_image(hotspot_instance, image)
        return image

    def post_process_image(self, image):
        return image

    @property
    def image(self):
        if not self.update_cached_images:
            logger.debug("Not caching images anymore - returning")
            return

        start = time.time()

        im = self.post_process_image(self.process_image(self.get_preprocess_image()))

        end = time.time()
        logger.debug(f"Time generating image: {end - start}")

        return im
