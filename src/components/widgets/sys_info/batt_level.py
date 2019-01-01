#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import subprocess
from components.widgets.common.base_widget_hotspot import BaseSnapshot


def get_battery():
    try:
        cmd = subprocess.Popen(["pt-battery", "-c"], stdout=subprocess.PIPE)
        response = cmd.communicate()
    except (FileNotFoundError, subprocess.CalledProcessError):
        response = "TEST"

    return str(response + "%")


def render(draw, width, height):
    draw.text((width/10, height/10), text=get_battery(), fill="white")


class Snapshot(BaseSnapshot):
    def __init__(self, width, height, interval, render_func):
        super(Snapshot, self).__init__(width, height, interval, render)

