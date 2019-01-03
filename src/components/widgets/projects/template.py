#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, **data):
        super(Hotspot, self).__init__(draw_fn=self.render, **data)

        self.title = data.get("title")
        self.img_path = data.get("img_path")

    def render(self, draw, width, height):
        w, h = draw.textsize(self.title)
        draw.text((width/2 - w/2, height - h*3/2), text=self.title, fill="white")

        if self.img_path != "":
            img_bitmap = Image.open(self.img_path).convert("RGBA")
            draw.bitmap((width/4, height/6), img_bitmap.resize((int(width/2), int(height/2))), fill="white")
