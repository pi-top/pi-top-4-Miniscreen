import logging

import PIL.ImageDraw
import PIL.ImageFont
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


def position_generator(max_value):
    DELTA_WIDTH_PX = 3
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
    def __init__(self, interval, size, mode, text, font=None, font_size=20):
        super().__init__(interval, size, mode)
        self.assistant = MiniscreenAssistant(self.mode, self.size)

        self.font_size = font_size

        if font is None:
            font = self.assistant.get_recommended_font(font_size)
        self.font = font
        self.text = text

    def render(self, image):
        if self.text == "":
            return

        x_coord = next(self.coordinate_generator)
        cropped_text_image = self.text_image.crop(
            (x_coord, 0) + (x_coord + self.size[0], self.text_image.height)
        )
        image.paste(cropped_text_image, (0, 0))

    @property
    def text(self):
        if callable(self._text):
            return self._text()
        return self._text

    @text.setter
    def text(self, value_or_callback):
        self._text = value_or_callback
        self.update_text_image()

    def update_text_image(self):
        # create empty image with the size of the text
        draw = PIL.ImageDraw.Draw(PIL.Image.new(self.mode, self.size, color="black"))
        text_bounding_box = draw.textbbox((0, 0), text=self.text, font=self.font)
        text_image_size = (
            text_bounding_box[2] - text_bounding_box[0],
            max(text_bounding_box[3] - text_bounding_box[1], self.size[1]),
        )
        self.text_image = PIL.Image.new(self.mode, text_image_size, color="black")

        # write text
        text_draw = PIL.ImageDraw.Draw(self.text_image)
        text_draw.text(xy=(0, 0), text=self.text, font=self.font, fill="white")

        # update coordinate generator maximum values for the new image
        self.coordinate_generator = pause_every(
            interval=self.text_image.width - self.size[0],
            generator=position_generator(self.text_image.width - self.size[0]),
            sleep_for=4,
        )
