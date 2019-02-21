# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import ImageFont
import os.path


tiny_font = ImageFont.truetype(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "FreePixel.ttf")
    ),
    10,
)


def right_text(draw, y, width, margin, text):
    x = width - margin - draw.textsize(text, font=tiny_font)[0]
    draw.text((x, y), text=text, font=tiny_font, fill="white")


def title_text(draw, y, width, text):
    x = (width - draw.textsize(text)[0]) / 2
    draw.text((x, y), text=text, fill="yellow")
