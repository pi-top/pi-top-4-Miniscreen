#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import time
from luma.core.virtual import hotspot
from hotspot.common import title_text
import sys

def render(draw, width, height):
    percentage = str(100) +"%"
    top_margin = 3
    bottom_margin = 3
    draw.text((width/10, height/10), text=percentage, fill="white")




class Battery_level(hotspot):

    def __init__(self, width, height, interval):
        super(Battery_level, self).__init__(width, height)
        self._interval = interval
        self._last_updated = 0

    def should_redraw(self):
        return time.time() - self._last_updated > self._interval

    def update(self, draw):
        render(draw, self.width, self.height)
        self._last_updated = time.time()
