import logging
from functools import lru_cache

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from pt_miniscreen.utils import get_font

from ...state import Speeds
from ..base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


def get_text_size(text, font):
    draw = PIL.ImageDraw.Draw(PIL.Image.new("1", (0, 0), color="black"))
    bounding_box = draw.textbbox(
        (0, 0),
        text=text,
        font=font,
    )
    return (
        bounding_box[2] - bounding_box[0],
        bounding_box[3] - bounding_box[1],
    )


def create_wrapped_text(text, font, max_width):
    words = text.split(" ")
    words.reverse()  # reverse words to avoid costly list operations later
    lines = [words.pop()]  # setup first line to equal first word

    while len(words) > 0:
        word = words.pop()

        # try adding word to the current line and move onto next word if it fits
        line = f"{lines[-1]} {word}"
        if get_text_size(line, font)[0] < max_width:
            lines[-1] = line
            continue

        # word doesn't fit on current line so use it to create next line
        lines.append(word)

    return "\n".join(lines)


class Hotspot(HotspotBase):
    def __init__(
        self,
        size,
        text,
        font=None,
        font_size=20,
        fill=1,
        align="left",
        vertical_align="top",
        bold=False,
        italics=False,
        spacing=0,
        wrap=True,
        interval=Speeds.DYNAMIC_PAGE_REDRAW.value,
    ):
        super().__init__(interval=interval, size=size)

        self._text = text
        self.font = font
        self.font_size = font_size
        self.fill = fill
        self.bold = bold
        self.italics = italics
        self.align = align
        self.vertical_align = vertical_align
        self.spacing = spacing
        self.wrap = wrap

        # Memoize expensive methods
        self.get_text_size = lru_cache(get_text_size)
        self.create_wrapped_text = lru_cache(create_wrapped_text)

    @property
    def font(self):
        if self._font:
            return self._font

        return get_font(self.font_size, self.bold, self.italics)

    @font.setter
    def font(self, _font):
        self._font = _font

    @property
    def text(self):
        if self.wrap:
            return self.create_wrapped_text(self._text, self.font, self.size[0])

        return self._text

    @text.setter
    def text(self, _text):
        self._text = _text

    @property
    def text_size(self):
        return self.get_text_size(self.text, self.font)

    @property
    def text_x(self):
        if self.align == "center":
            return int((self.size[0] - self.text_size[0]) / 2)

        if self.align == "right":
            return self.size[0] - self.text_size[0]

        return 0

    @property
    def text_y(self):
        if self.vertical_align == "center":
            return int((self.size[1] - self.text_size[1]) / 2)

        if self.vertical_align == "bottom":
            return self.size[1] - self.text_size[1]

        return 0

    @property
    def text_pos(self):
        return (self.text_x, self.text_y)

    def render(self, image):
        # multiline doesn't support anchor so pass none if any newlines found
        anchor = "lt" if "\n" not in self.text else None

        PIL.ImageDraw.Draw(image).text(
            text=self.text,
            xy=self.text_pos,
            font=self.font,
            fill=self.fill,
            spacing=self.spacing,
            align=self.align,
            anchor=anchor,
        )
