from os import path

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from pt_miniscreen.utils import get_project_root

from .values import right_text_default_margin


def get_image_file_path(relative_file_name):
    return path.abspath(path.join(get_project_root(), "images", relative_file_name))


def get_font(size=12):
    # Hard-code OLED properties for simple import
    assistant = MiniscreenAssistant("1", (128, 64))

    return assistant.get_recommended_font(size=size)


def draw_text(
    draw,
    xy,
    text,
    fill=1,
    font=None,
    anchor=None,
    spacing=0,
    align="left",
    features=None,
    font_size=12,
):
    if font is None:
        font = get_font(font_size)
    draw.text(
        xy=xy,
        text=text,
        fill=fill,
        font=font,
        anchor=anchor,
        spacing=spacing,
        align=align,
        features=features,
    )


def right_text(draw, y, width, text, margin=right_text_default_margin):
    x = width - margin - draw.textsize(text)[0]
    draw_text(draw, xy=(x, y), text=text)


def title_text(draw, y, width, text):
    x = align_to_middle(draw, width=width, text=text)
    draw_text(draw, xy=(x, y), text=text)


def align_to_middle(draw, width, text):
    return (width - draw.textsize(text)[0]) / 2


def process_image(image_to_process, size, mode):
    if image_to_process.size == size:
        image = image_to_process
        if image.mode != mode:
            image = image.convert(mode)
    else:
        image = Image.new(mode, size, "black")
        image.paste(image_to_process.resize(size, resample=Image.NEAREST))

    return image
