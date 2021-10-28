import logging

import PIL.ImageDraw
import PIL.ImageFont
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


def position_generator(max_value):
    DELTA_WIDTH_PX = 10
    while True:
        if max_value <= 0:
            yield 0
        else:
            for x in range(0, max_value, DELTA_WIDTH_PX):
                yield x
            for x in range(max_value, 0, -DELTA_WIDTH_PX):
                yield x


def pause_every(interval, generator, sleep_for):
    while True:
        x = next(generator)
        if x % interval == 0:
            for _ in range(sleep_for):
                yield x
        else:
            yield x


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode, text, font=None, font_size=20, xy=None):
        super().__init__(interval, size, mode)
        X_RIGHT_MARGIN = 10
        self.hotspot_width = size[0] - X_RIGHT_MARGIN
        self.assistant = MiniscreenAssistant(self.mode, self.size)

        self.font_size = font_size
        if xy is None:
            xy = (size[0] / 2, size[1] / 2)
        self.xy = xy

        if font is None:
            font = self.assistant.get_recommended_font(font_size)
        self.font = font

        self.text = text

    def render(self, image):
        if self.text == "":
            return

        x_coord = next(self.coordinate_generator)
        cropped_text_img = self.text_image.crop(
            (x_coord, 0) + (x_coord + self.hotspot_width, self.text_image.height)
        )
        image.paste(cropped_text_img, self.xy)

    @property
    def text(self):
        if callable(self._text):
            return self._text()
        return self._text

    @text.setter
    def text(self, value_or_callback):
        self._text = value_or_callback
        text_value = self.text

        # create empty image of the size of the text
        draw = PIL.ImageDraw.Draw(PIL.Image.new(self.mode, self.size, color="black"))
        text_bounding_box = draw.textbbox((0, 0), text=text_value, font=self.font)

        text_image_size = (
            text_bounding_box[2] - text_bounding_box[0],
            text_bounding_box[3] - text_bounding_box[1],
        )
        self.text_image = PIL.Image.new(self.mode, text_image_size, color="black")

        # draw text in the image's (0, 0)
        offset_to_origin = [
            abs(value) * (-1 if value > 0 else 1) for value in text_bounding_box[:2]
        ]
        text_draw = PIL.ImageDraw.Draw(self.text_image)
        text_draw.text(offset_to_origin, text_value, font=self.font, fill="white")

        # update coordinate generator maximum values for the given text
        self.coordinate_generator = pause_every(
            interval=self.text_image.width - self.hotspot_width,
            generator=position_generator(self.text_image.width - self.hotspot_width),
            sleep_for=2,
        )
