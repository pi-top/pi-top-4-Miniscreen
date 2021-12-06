import logging
from threading import Event, Thread
from time import sleep

from PIL import Image, ImageChops, ImageOps
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...event import AppEvent, post_event
from ...types import Coordinate

logger = logging.getLogger(__name__)


def have_differences(image_one: Image.Image, image_two: Image.Image) -> bool:
    try:
        return ImageChops.difference(image_one, image_two).getbbox() is not None
    except Exception:
        logger.debug(f"Error comparing images {image_one} and {image_two}")
        return False


class Hotspot:
    def __init__(self, interval: float, size: Coordinate):
        self._interval: float = interval
        self.size: Coordinate = size

        self.draw_white: bool = True
        self.draw_black: bool = False

        self.invert: bool = False
        self.width: int = size[0]
        self.height: int = size[1]

        self._cached_image = Image.new("1", self.size)

        self._active: bool = False
        self.is_active_event = Event()

        self.caching_thread = Thread(
            target=self._cache_image_on_interval_when_active, args=(), daemon=True
        )

    def start(self):
        self.caching_thread.start()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, is_active):
        self._active = is_active
        if self.active:
            self.is_active_event.set()

        if self.is_active_event.is_set():
            self.is_active_event.clear()

    @property
    def cached_image(self) -> Image.Image:
        return self._cached_image

    @cached_image.setter
    def cached_image(self, image: Image.Image) -> None:
        self._cached_image = image
        post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, interval: float) -> None:
        self._interval = interval

    @property
    def width(self) -> int:
        return self.size[0]

    @width.setter
    def width(self, value: int) -> None:
        self.size = (value, self.height)

    @property
    def height(self) -> int:
        return self.size[1]

    @height.setter
    def height(self, value: int) -> None:
        self.size = (self.width, value)

    @property
    def _raw_image(self) -> Image.Image:
        im = Image.new("1", self.size)

        if not self.draw_white and not self.draw_black:
            return im

        self.render(im)

        if self.invert:
            im = MiniscreenAssistant("1", self.size).invert(im)

        self.render(im)
        return im

    @property
    def image(self):
        return self.cached_image

    def render(self, image: Image.Image) -> None:
        raise NotImplementedError

    def _wait_until_active(self):
        if not self.active:
            logger.debug("Hotspot not active - waiting...")
            self.is_active_event.wait()
            logger.debug("Hotspot now active!")

    def _update_cached_image_if_new(self):
        image = self._raw_image
        if have_differences(self.image, image):
            self.cached_image = image
            post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    def _cache_image_on_interval_when_active(self):
        self._cached_image = self._raw_image
        while True:
            self._wait_until_active()
            self._update_cached_image_if_new()

            sleep(self.interval)

    def get_mask(self, image: Image.Image) -> Image.Image:
        """Get a bitwise XNOR pixel mask for a given PIL image, based on the
        hotspot's masking parameters (draw_{white,black}).

        Use like so with a PIL Image:
        ```
        im = hotspot.image
        image.paste(
            im,
            xy,
            hotspot.get_mask(im)
        )
        ```
        """

        # 'superimpose'
        white_only = self.draw_white and not self.draw_black

        # 'paste over'
        white_and_black = self.draw_black and not self.draw_white

        # 'inverted superimpose'
        black_only = self.draw_black and not self.draw_white

        if white_only:
            mask = image

        elif black_only:
            mask = ImageOps.invert(image)

        elif white_and_black:
            mask = Image.new("1", size=image.size, color="white")

        else:  # nothing (no effect) = not self.draw_black and not self.draw_black
            mask = Image.new("1", size=image.size, color="black")

        return mask
