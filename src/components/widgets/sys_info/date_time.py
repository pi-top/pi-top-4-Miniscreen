#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import datetime
from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        date_time = datetime.datetime.now()
        date = str(date_time.day) + "/" + str(date_time.month) + "/" + str(date_time.year)
        time = str(date_time.hour) + ":" + str(date_time.minute) + ":" + str(date_time.second)

        title_text(draw, height / 10, width, date)

        draw.text((width / 3, height / 3), text=time, fill="white")