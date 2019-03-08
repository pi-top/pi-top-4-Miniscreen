# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.formatting import bytes2human
import psutil
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common_values import default_margin_x, default_margin_y
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        df = psutil.disk_usage("/")

        title_text(draw, default_margin_y, width, text="Disk")
        draw_text(draw, xy=(default_margin_x, height / common_first_line_y), text="Used:")
        draw_text(draw, xy=(default_margin_x, height / common_second_line_y), text="Free:")
        draw_text(draw, xy=(default_margin_x, height / common_third_line_y), text="Total:")

        right_text(draw, height / common_first_line_y, width, text="{0:0.1f}%".format(df.percent))
        right_text(draw, height / common_second_line_y, width, text=bytes2human(df.free, "{0:0.0f}"))
        right_text(draw, height / common_third_line_y, width, text=bytes2human(df.total, "{0:0.0f}"))
