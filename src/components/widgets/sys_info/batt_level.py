#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import subprocess
from components.widgets.common.base_widget_hotspot import BaseHotspot


def get_battery():
    try:
        battery_level = str(subprocess.check_output(["pt-battery", "-c"]).decode("utf-8")).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        battery_level = "TEST"

    return str(battery_level + "%")


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        draw.text((width / 10, height / 10), text=get_battery(), fill="white")
