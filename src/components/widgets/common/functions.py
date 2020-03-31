from PIL import ImageFont
from os import path
from components.widgets.common.values import default_margin_x, right_text_default_margin


def get_image_file(relative_file_name):
    return path.abspath(
        path.join("/usr", "share", "pt-sys-oled", "images", relative_file_name)
    )


def get_font(size=12):

    if size >= 12:
        font = ImageFont.truetype(
            "/usr/share/fonts/opentype/FSMePro/FSMePro-Light.otf", size
        )
    else:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf", size
        )
    return font


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
