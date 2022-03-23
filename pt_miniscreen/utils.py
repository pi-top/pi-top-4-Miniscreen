from os import path
from pathlib import Path

from PIL import ImageFont


def get_project_root() -> Path:
    return Path(__file__).parent


def get_image_file_path(relative_file_name: str) -> str:
    return path.abspath(path.join(get_project_root(), "images", relative_file_name))


def get_mono_font(size, bold=False, italics=False):
    if bold and not italics:
        return ImageFont.truetype("VeraMoBd.ttf", size=size)

    if not bold and italics:
        return ImageFont.truetype("VeraMoIt.ttf", size=size)

    if bold and italics:
        return ImageFont.truetype("VeraMoBI.ttf", size=size)

    return ImageFont.truetype("VeraMono.ttf", size=size)


def get_font(size, bold=False, italics=False):
    if size >= 12:
        return ImageFont.truetype("Roboto-Regular.ttf", size=size)

    return get_mono_font(size, bold, italics)


def offset_to_center(container, element, rounding_function=int):
    return rounding_function((container - element) / 2)
