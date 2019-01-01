#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image
from components.widgets.common.base_widget_hotspot import BaseStaticHotspot


class StaticHotspot(BaseStaticHotspot):
    def __init__(self, width, height, **data):
        super(StaticHotspot, self).__init__(width, height, self.render)

        for key, value in data.items():
            if key == "title":
                self.title = value
            if key == "img_path":
                self.img_path = value

    def render(self, draw, width, height):
        w, h = draw.textsize(self.title)
        draw.text((width/2 - w/2, height - h*3/2), text=self.title, fill="white")

        if self.img_path != "":
            img_bitmap = Image.open(self.img_path).convert("RGBA")
            draw.bitmap((width/4, height/6), img_bitmap.resize((int(width/2), int(height/2))), fill="white")