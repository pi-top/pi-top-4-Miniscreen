# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from ptcommon.formatting import bytes2human
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

        margin = 3

        title_text(draw, margin, width, text="Memory")
        draw_text(draw, x=margin, y=20, text="Used:")
        draw_text(draw, x=margin, y=35, text="Phys:")
        draw_text(draw, x=margin, y=45, text="Swap:")

        right_text(draw, 20, width, margin, text="{0:0.1f}%".format(mem_used_pct))
        right_text(draw, 35, width, margin, text=bytes2human(mem.used))
        right_text(draw, 45, width, margin, text=bytes2human(swap.used))
