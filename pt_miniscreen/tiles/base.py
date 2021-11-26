import logging
import time
from threading import Thread
from time import sleep
from typing import Dict, List

from PIL import Image, ImageChops
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..event import AppEvents, post_event
from ..hotspots.base import HotspotInstance

logger = logging.getLogger(__name__)


class Tile:
    def __init__(self, size, pos=(0, 0)) -> None:
        self._size = size
        self._pos = pos
        self.cached_images: Dict = dict()
        self.image_caching_threads: Dict = dict()
        self.active = False
        self.hotspot_instances: List[HotspotInstance] = list()
        self._render_size = self.size

        self.reset()

    def reset(self):
        pass

    @property
    def window_position(self):
        return (0, 0)

    @property
    def size(self):
        if callable(self._size):
            return self._size()

        return self._size

    @size.setter
    def size(self, xy):
        size = xy
        if callable(xy):
            size = xy()

        if size == self.size:
            return

        self._size = xy
        self.reset()

    @property
    def pos(self):
        if callable(self._pos):
            return self._pos()

        return self._pos

    @pos.setter
    def pos(self, xy):
        self._pos = xy

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

    def start(self):
        for _, thread in self.image_caching_threads.items():
            thread.start()

    def stop(self):
        if len(self.image_caching_threads) == 0:
            return

        logger.debug(
            f"Tile: stopping {len(self.image_caching_threads)} hotspot threads..."
        )
        for _, thread in self.image_caching_threads.items():
            thread.do_run = False
            thread.join(0)

        logger.debug(f"Tile: stopped {len(self.image_caching_threads)} hotspot threads")
        self.image_caching_threads = dict()

    def _paste_hotspot_into_image(self, hotspot_instance, image):
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
                "1", hotspot_instance.hotspot.size
            ).invert(hotspot_image)

        mask = hotspot_instance.hotspot.mask(hotspot_image)
        pos = hotspot_instance.xy
        # box = pos + (pos[0] + hotspot_image.size[0], pos[1] + hotspot_image.size[1])
        # logger.debug(
        #     f"viewport.paste_hotspot_into_image - hotspot image size: {hotspot_image.size}"
        # )
        # logger.debug(
        #     f"viewport.paste_hotspot_into_image - base image size: {image.size}"
        # )
        # logger.debug(
        #     f"viewport.paste_hotspot_into_image - hotspot xy: {hotspot_instance.xy}"
        # )
        # logger.debug(f"viewport.paste_hotspot_into_image - position: {pos}")
        image.paste(hotspot_image, pos, mask)

    def set_hotspot_instances(self, hotspot_instances, start=False):
        self.clear()
        logger.info(f"Adding {len(hotspot_instances)} hotspot instances...")
        for hotspot_instance in hotspot_instances:
            self.add_hotspot_instance(hotspot_instance)
        if start:
            logger.info(
                f"Automatically starting {len(hotspot_instances)} hotspot instances..."
            )
            self.start()

    def add_hotspot_instance(self, hotspot_instance):
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
        self.cached_images[hotspot_instance.hotspot] = None

        self._register_thread(hotspot_instance)

    def remove_hotspot_instance(self, hotspot_instance):
        self.hotspot_instances.remove(hotspot_instance)

    def _register_thread(self, hotspot_instance):
        # logger.debug(f"Registering image caching thread for hotspot_instance {hotspot_instance}...")
        hotspot = hotspot_instance.hotspot

        def run():
            def have_differences(image_one, image_two):
                try:
                    return (
                        ImageChops.difference(image_one, image_two).getbbox()
                        is not None
                    )
                except Exception:
                    logger.debug(f"Error comparing images {image_one} and {image_two}")
                    return False

            def cache_new_image():
                last_img = self.cached_images[hotspot]
                new_img = hotspot.image
                if last_img is None or have_differences(last_img, new_img):
                    self.cached_images[hotspot] = new_img
                    post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

            # logger.debug("Caching new image...")
            cache_new_image()
            # logger.debug(f"Done caching new image : {self.update_cached_images}")

            while True:
                # TODO: improve this "busy wait"
                # if not active, there's no need to check - perhaps instead of sleeping,
                # we should wait on an event triggered on active state change?
                #
                # another thing to consider would be to do something similar with 'is overlapping'
                # - if we are not overlapping, and the position is not changing, then this is still
                # busy waiting...
                if self.active and self.is_hotspot_overlapping(hotspot_instance):
                    cache_new_image()
                sleep(hotspot.interval)

        self.image_caching_threads[hotspot] = Thread(
            target=run, args=(), daemon=True, name=hotspot
        )

    def clear(self):
        self.stop()
        self.remove_all_hotspot_instances()

    def remove_all_hotspot_instances(self):
        if len(self.hotspot_instances) == 0:
            return

        logger.warning(f"Removing {len(self.hotspot_instances)} hotspot instances...")
        self.hotspot_instances = list()

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

    @property
    def render_size(self):
        return (
            self._render_size
            if self._render_size[0] > self.size[0]
            or self._render_size[1] > self.size[1]
            else self.size
        )

    def get_preprocess_image(self):
        return Image.new("1", self.render_size)

    def process_image(self, image):
        for hotspot_instance in self.hotspot_instances:
            if not self.is_hotspot_overlapping(hotspot_instance):
                continue
            self._paste_hotspot_into_image(hotspot_instance, image)
        return image

    def post_process_image(self, image):
        return image if image.size == self.size else image.crop(box=(0, 0) + self.size)

    @property
    def image(self):
        im = self.get_preprocess_image()

        if not self.active:
            logger.debug("Not active - returning")
            return im

        start = time.time()

        im = self.post_process_image(self.process_image(im))

        end = time.time()
        logger.debug(f"Time generating image: {end - start}")

        return im

    def handle_select_btn(self):
        return

    def handle_cancel_btn(self):
        return

    def handle_up_btn(self):
        return

    def handle_down_btn(self):
        return
