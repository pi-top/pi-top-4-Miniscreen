import PIL.Image
import PIL.ImageDraw
import linecache
from enum import Enum, auto
from os import path
from pathlib import Path
from functools import partial
from pt_miniscreen.core.components.text import create_wrapped_text

from pt_miniscreen.core.utils import get_font

VIEWPORT_HEIGHT = 64
VIEWPORT_WIDTH = 128
VIEWPORT_SIZE = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT)


def get_project_root() -> Path:
    return Path(__file__).parent


def get_image_file_path(relative_file_name: str) -> str:
    return path.abspath(path.join(get_project_root(), "images", relative_file_name))


def isclass(obj, cls) -> bool:
    return (
        isinstance(obj, partial)
        and issubclass(obj.func, cls)  # type: ignore
        or isinstance(obj, cls)
    )


class ButtonEvents(Enum):
    UP_PRESS = auto()
    UP_RELEASE = auto()
    DOWN_PRESS = auto()
    DOWN_RELEASE = auto()
    CANCEL_PRESS = auto()
    CANCEL_RELEASE = auto()
    SELECT_PRESS = auto()
    SELECT_RELEASE = auto()


class TextFile:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.len = 0

        if Path(filename).exists():
            with open(self.filename) as f:
                for _ in f:
                    self.len += 1

    def line(self, line_number: int):
        return linecache.getline(self.filename, line_number)

    def range(self, start_line: int, end_line: int):
        return [
            linecache.getline(self.filename, line_number)
            for line_number in range(start_line, end_line)
        ]


def text_to_image(
    text,
    width=VIEWPORT_WIDTH,
    font=None,
    font_size=8,
    fill=1,
    align="left",
    bold=False,
    italics=False,
    spacing=2,
    wrap=True,
    wrap_margin=0,
) -> PIL.Image.Image:
    image = PIL.Image.new("1", (width, 10))
    font = get_font(font_size, bold, italics) if font is None else font
    if wrap:
        text = create_wrapped_text(text, font, image.width - wrap_margin)

    # Draw text and get its size
    text_box = PIL.ImageDraw.Draw(image).textbbox(
        text=text,
        xy=(0, 0),
        font=font,
        spacing=spacing,
        align=align,
    )

    text_height = text_box[3] - text_box[1]
    image = PIL.Image.new("1", (width, text_height))
    PIL.ImageDraw.Draw(image).text(
        text=text,
        xy=(0, 0),
        font=font,
        fill=fill,
        spacing=spacing,
        align=align,
    )
    return image
