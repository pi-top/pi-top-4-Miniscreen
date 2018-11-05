#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import time
from luma.core.virtual import hotspot
import datetime
from hotspot.common import title_text


def render(draw, width, height):
    date_time = datetime.datetime.now()
    date = str(date_time.day) + "/" + str(date_time.month) + "/" + str(date_time.year)
    time = str(date_time.hour) + ":" + str(date_time.minute) + ":" + str(date_time.second)

    title_text(draw, height/10, width, date)

    draw.text((width/3, height/3), text=time, fill="white")

class DateTime(hotspot):

    def __init__(self, width, height, interval):
        super(DateTime, self).__init__(width, height)
        self._interval = interval
        self._last_updated = 0

    def should_redraw(self):
        return time.time() - self._last_updated > self._interval

    def update(self, draw):
        render(draw, self.width, self.height)
        self._last_updated = time.time()
