import logging
from typing import Iterator

from PIL import Image, ImageDraw

from pt_miniscreen.utils import get_font

from ...generators import carousel, pause_every
from ...state import Speeds
from ...types import Coordinate
from ..base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    DELTA_PX = 2

    def __init__(
        self,
        size: Coordinate,
        text: str,
        font=None,
        font_size: int = 20,
        interval: float = Speeds.MARQUEE.value,
    ):
        super().__init__(interval=interval, size=size)

        self.coordinate_generator: Iterator = iter(())
        self.text_image = Image.new("1", self.size, color="black")

        self._interval = interval
        self.font_size = font_size

        if font is None:
            font = get_font(font_size)
        self.font = font
        self._text = text
        self._update_text_image()

    def render(self, image: Image.Image) -> None:
        if self.text == "":
            return

        try:
            x_coord = next(self.coordinate_generator)
        except StopIteration:
            x_coord = 0

        cropped_text_image = self.text_image.crop(
            (x_coord, 0) + (x_coord + self.size[0], self.text_image.height)
        )
        image.paste(cropped_text_image, (0, 0))

    def _update_text_image(self) -> None:
        # create empty image with the size of the text
        draw = ImageDraw.Draw(Image.new("1", self.size, color="black"))
        text_bounding_box = draw.textbbox((0, 0), text=self.text, font=self.font)
        text_image_size = (
            text_bounding_box[2] - text_bounding_box[0],
            max(text_bounding_box[3] - text_bounding_box[1], self.size[1]),
        )
        self.text_image = Image.new("1", text_image_size, color="black")

        # write text
        text_draw = ImageDraw.Draw(self.text_image)
        text_draw.text(xy=(0, 0), text=self.text, font=self.font, fill="white")

        scroll_len = self.text_image.width - self.size[0]

        # update coordinate generator maximum values for the new image
        self.coordinate_generator = pause_every(
            pause_yield_interval=scroll_len,
            generator=carousel(
                min_value=0,
                max_value=scroll_len,
                resolution=self.DELTA_PX,
            ),
            no_of_pause_yields=8,
        )

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_text) -> None:
        if new_text == self.text:
            return

        self._text = new_text
        self._update_text_image()

    @property
    def needs_scrolling(self) -> bool:
        try:
            return self.width <= self.text_image.width
        except Exception:
            return False

    @property
    def interval(self) -> float:
        if not self.needs_scrolling:
            return Speeds.DYNAMIC_PAGE_REDRAW.value
        return self._interval

    @interval.setter
    def interval(self, interval: float) -> None:
        self._interval = interval
