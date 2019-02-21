# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.formatting import bytes2human
import psutil
from components.widgets.common_functions import right_text, title_text, tiny_font
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        df = psutil.disk_usage("/")

        margin = 3

        title_text(draw, margin, width, text="Disk")
        draw.text((margin, 20), text="Used:", font=tiny_font, fill="white")
        draw.text((margin, 35), text="Free:", font=tiny_font, fill="white")
        draw.text((margin, 45), text="Total:", font=tiny_font, fill="white")

        right_text(draw, 20, width, margin, text="{0:0.1f}%".format(df.percent))
        right_text(draw, 35, width, margin, text=bytes2human(df.free, "{0:0.0f}"))
        right_text(draw, 45, width, margin, text=bytes2human(df.total, "{0:0.0f}"))
