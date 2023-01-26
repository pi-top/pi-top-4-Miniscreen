import PIL.Image
import PIL.ImageDraw
from enum import Enum, auto
from os import path
from pathlib import Path
from functools import partial
from pt_miniscreen.core.components.text import create_wrapped_text

from pt_miniscreen.core.utils import get_font


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


def file_to_image(
    path,
    width=128,
    font=None,
    font_size=20,
    fill=1,
    align="left",
    bold=False,
    italics=False,
    spacing=0,
    wrap=True,
) -> PIL.Image.Image:

    # Read file
    with open(path, "r") as f:
        text = f.read()

    image = PIL.Image.new("1", (width, 10))
    font = get_font(font_size, bold, italics) if font is None else font
    if wrap:
        text = create_wrapped_text(text, font, image.width)

    # Multiline doesn't support anchor so pass none if any newlines found
    anchor = "lt" if "\n" not in text else None

    # Draw text and get its size
    text_size = PIL.ImageDraw.Draw(image).textsize(
        text=text,
        font=font,
        spacing=spacing,
    )

    # Create new image with the text size
    image = PIL.Image.new("1", text_size)
    PIL.ImageDraw.Draw(image).text(
        text=text,
        xy=(0, 0),
        font=font,
        fill=fill,
        spacing=spacing,
        align=align,
        anchor=anchor,
    )

    # Crop image to fit provided width
    return image.crop(
        ((image.width - width) / 2, 0, image.width / 2 + width, image.height)
    )
