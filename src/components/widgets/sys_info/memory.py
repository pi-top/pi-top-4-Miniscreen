# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from ptcommon.formatting import bytes2human
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common_values import default_margin
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

        title_text(draw, y=default_margin, width=width, text="Memory")
        draw_text(draw, xy=(default_margin, 20), text="Used:")
        draw_text(draw, xy=(default_margin, 35), text="Phys:")
        draw_text(draw, xy=(default_margin, 50), text="Swap:")

        right_text(draw, 20, width, text="{0:0.1f}%".format(mem_used_pct))
        right_text(draw, 35, width, text=bytes2human(mem.used))
        right_text(draw, 50, width, text=bytes2human(swap.used))
