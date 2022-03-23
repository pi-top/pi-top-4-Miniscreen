import logging
from functools import lru_cache

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from pt_miniscreen.core.utils import get_font

from .. import Hotspot

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


class Text(Hotspot):
    size = (0, 0)

    def __init__(
        self,
        text="",
        get_text=None,
        get_text_lazily=False,
        font=None,
        font_size=20,
        fill=1,
        align="left",
        vertical_align="top",
        bold=False,
        italics=False,
        spacing=0,
        wrap=True,
        get_text_interval=1,
        initial_state={},
        **kwargs,
    ):
        text = get_text() if callable(get_text) and not get_text_lazily else text
        font = get_font(font_size, bold, italics) if font is None else font
        self._get_text = get_text

        super().__init__(
            **kwargs,
            initial_state={
                "text": text,
                "font": font,
                "fill": fill,
                "align": align,
                "vertical_align": vertical_align,
                "spacing": spacing,
                "wrap": wrap,
                **initial_state,
            },
        )

        # Memoize expensive methods
        self.get_text_size = lru_cache(get_text_size)
        self.create_wrapped_text = lru_cache(create_wrapped_text)

        # start polling text if get_text is callable
        if callable(self._get_text):
            self.create_interval(self._update_text, get_text_interval)

    def _update_text(self):
        self.state.update({"text": self._get_text()})

    def _calculate_text_x(self, text, font, width):
        text_size = self.get_text_size(text, font)

        if self.state["align"] == "center":
            return int((width - text_size[0]) / 2)

        if self.state["align"] == "right":
            return width - text_size[0]

        return 0

    def _calculate_text_y(self, text, font, height):
        text_size = self.get_text_size(text, font)

        if self.state["vertical_align"] == "center":
            return int((height - text_size[1]) / 2)

        if self.state["vertical_align"] == "bottom":
            return height - text_size[1]

        return 0

    def render(self, image):
        font = self.state["font"]

        text = self.state["text"]
        if self.state["wrap"]:
            text = self.create_wrapped_text(text, font, image.width)

        xy = (
            self._calculate_text_x(text, font, image.width),
            self._calculate_text_y(text, font, image.height),
        )

        # multiline doesn't support anchor so pass none if any newlines found
        anchor = "lt" if "\n" not in text else None

        PIL.ImageDraw.Draw(image).text(
            text=text,
            xy=xy,
            font=font,
            fill=self.state["fill"],
            spacing=self.state["spacing"],
            align=self.state["align"],
            anchor=anchor,
        )

        return image
