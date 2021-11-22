import logging

import PIL.ImageDraw
import PIL.ImageFont
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(
        self,
        interval,
        size,
        mode,
        text,
        font_size=20,
        xy=None,
        font=None,
        fill=1,
        anchor=None,
        align=None,
    ):
        super().__init__(interval, size, mode)

        self.assistant = MiniscreenAssistant(self.mode, self.size)
        self._text = text
        self.font_size = font_size

        if xy is None:
            xy = (int(size[0] / 2), int(size[1] / 2))
        self.xy = xy
        self.anchor = anchor
        self.align = align

        if font is None:
            font = self.assistant.get_recommended_font_path(self.font_size)
        self.font = font
        self.fill = fill

    def render(self, image):
        self.assistant.render_text(
            image,
            text=self.text,
            xy=self.xy,
            font_size=self.font_size,
            font=self.font,
            fill=self.fill,
            anchor=self.anchor,
            align=self.align,
        )

    @property
    def text(self):
        if callable(self._text):
            return self._text()
        return self._text

    @text.setter
    def text(self, value_or_callback):
        self._text = value_or_callback

    @property
    def text_size(self):
        draw = PIL.ImageDraw.Draw(PIL.Image.new(self.mode, self.size, color="black"))
        text_bounding_box = draw.textbbox(
            (0, 0),
            text=self.text,
            font=PIL.ImageFont.truetype(self.font, size=self.font_size),
        )
        return (
            text_bounding_box[2] - text_bounding_box[0],
            min(text_bounding_box[3] - text_bounding_box[1], self.height),
        )
