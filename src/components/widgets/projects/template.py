#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image

def project(title="My Project", img_path=""):
    def render(draw, width, height):
        w, h = draw.textsize(title)
        draw.text((width/2 - w/2, height - h*3/2), text=title, fill="white")

        if img_path != "":
            img_bitmap = Image.open(img_path).convert("RGBA")
            draw.bitmap((width/4, height/6), img_bitmap.resize((width/2, height/2)), fill="white")

    return render