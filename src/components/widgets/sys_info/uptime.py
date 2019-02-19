#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from datetime import datetime
import psutil
from components.widgets.common_functions import title_text, right_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        elapsed = datetime.now() - boot_time
        margin = 3
        title_text(draw, margin, width, "Uptime")
        right_text(
            draw, 20, width, margin, text="{0} s".format(int(elapsed.total_seconds()))
        )
