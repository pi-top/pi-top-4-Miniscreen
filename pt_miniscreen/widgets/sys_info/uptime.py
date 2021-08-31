# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from datetime import datetime

import psutil

from pt_miniscreen.widgets.common import (
    BaseSnapshot,
    default_margin_y,
    right_text,
    title_text,
)


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        elapsed = datetime.now() - boot_time
        title_text(draw, default_margin_y, width, "Uptime")
        time = "{0} s".format(int(elapsed.total_seconds()))
        right_text(draw, y=height / 2, width=width, text=time)
