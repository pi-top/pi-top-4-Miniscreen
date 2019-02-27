# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.formatting import bytes2human
import psutil
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        df = psutil.disk_usage("/")

        margin = 3

        title_text(draw, margin, width, text="Disk")
        draw_text(draw, x=margin, y=20, text="Used:")
        draw_text(draw, x=margin, y=35, text="Free:")
        draw_text(draw, x=margin, y=45, text="Total:")

        right_text(draw, 20, width, margin, text="{0:0.1f}%".format(df.percent))
        right_text(draw, 35, width, margin, text=bytes2human(df.free, "{0:0.0f}"))
        right_text(draw, 45, width, margin, text=bytes2human(df.total, "{0:0.0f}"))
