import logging
import time
from threading import Thread
from time import sleep
from typing import Dict, List

from PIL import Image, ImageChops

from ..event import AppEvent, post_event
from ..hotspots.base import Hotspot, HotspotInstance
from ..types import BoundingBox, CachedImage, Coordinate

logger = logging.getLogger(__name__)


class Tile:
    def __init__(self, size: Coordinate, pos: Coordinate = (0, 0)) -> None:
        self._size: Coordinate = size
        self.pos: Coordinate = pos
        self.cached_images: Dict[Hotspot, CachedImage] = dict()
        self.image_caching_threads: Dict[Hotspot, Thread] = dict()
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

    def start(self) -> None:
        for _, thread in self.image_caching_threads.items():
            thread.start()

    def stop(self) -> None:
        if len(self.image_caching_threads) == 0:
            return

        logger.debug(
            f"Tile: stopping {len(self.image_caching_threads)} hotspot threads..."
        )
        for _, thread in self.image_caching_threads.items():
            setattr(thread, "do_run", False)
            thread.join(0)

        logger.debug(f"Tile: stopped {len(self.image_caching_threads)} hotspot threads")
        self.image_caching_threads = dict()

    def _paste_hotspot_into_image(
        self, hotspot_instance: HotspotInstance, image: Image.Image
    ) -> None:
        if (
            not hotspot_instance.hotspot.draw_white
            and not hotspot_instance.hotspot.draw_black
        ):
            return

        if hotspot_instance.hotspot not in self.cached_images:
            return

        image.paste(
            self.cached_images[hotspot_instance.hotspot][0],  # .convert("1"),
            hotspot_instance.xy,
            self.cached_images[hotspot_instance.hotspot][1],  # .convert("1"),
        )

    def set_hotspot_instances(
        self, hotspot_instances: List[HotspotInstance], start: bool = False
    ) -> None:
        self.clear()
        logger.debug(f"Adding {len(hotspot_instances)} hotspot instances...")
        for hotspot_instance in hotspot_instances:
            self.add_hotspot_instance(hotspot_instance)
        if start:
            logger.debug(
                f"Automatically starting {len(hotspot_instances)} hotspot instances..."
            )
            self.start()

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

        self.cached_images[
            hotspot_instance.hotspot
        ] = hotspot_instance.hotspot.get_cached_image()

        self._register_thread(hotspot_instance)

    def remove_hotspot_instance(self, hotspot_instance: HotspotInstance):
        self.hotspot_instances.remove(hotspot_instance)

    def _register_thread(self, hotspot_instance: HotspotInstance):
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
                last_img = self.cached_images[hotspot][0]
                new_img, new_mask = hotspot_instance.hotspot.get_cached_image()
                if last_img is None or have_differences(last_img, new_img):
                    self.cached_images[hotspot] = (new_img, new_mask)
                    post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

            while True:
                # Wait until active
                if not self.active:
                    self.is_active_event.wait()
                    self.is_active_event.clear()

                # If not overlapping, wait until conditions change
                if not self.is_hotspot_overlapping(hotspot_instance):
                    # self.overlap_conditions_changed = Event()
                    self.overlap_conditions_changed.wait()
                    self.overlap_conditions_changed.clear()

                # Conditions may be correct - check if overlapping
                if self.is_hotspot_overlapping(hotspot_instance):
                    cache_new_image()

                    sleep(hotspot.interval)

        self.image_caching_threads[hotspot] = Thread(target=run, args=(), daemon=True)

    def clear(self) -> None:
        self.stop()
        self.remove_all_hotspot_instances()

    def remove_all_hotspot_instances(self) -> None:
        if len(self.hotspot_instances) == 0:
            return

        logger.debug(f"Removing {len(self.hotspot_instances)} hotspot instances...")
        self.hotspot_instances = list()

    def is_hotspot_overlapping(self, hotspot_instance: HotspotInstance) -> bool:
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
    def render_size(self) -> Coordinate:
        return (
            self._render_size
            if self._render_size[0] > self.size[0]
            or self._render_size[1] > self.size[1]
            else self.size
        )

    def get_preprocess_image(self) -> Image.Image:
        return Image.new("1", self.render_size)

    def process_image(self, image: Image.Image) -> Image.Image:
        for hotspot_instance in self.hotspot_instances:
            if not self.is_hotspot_overlapping(hotspot_instance):
                continue
            self._paste_hotspot_into_image(hotspot_instance, image)
        return image

    def post_process_image(self, image: Image.Image) -> Image.Image:
        return image if image.size == self.size else image.crop(box=(0, 0) + self.size)

    @property
    def image(self) -> Image.Image:
        im = self.get_preprocess_image()

        if not self.active:
            logger.debug("Not active - returning")
            return im

        start = time.time()

        im = self.post_process_image(self.process_image(im))

        end = time.time()
        logger.debug(f"Time generating image: {end - start}")

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
