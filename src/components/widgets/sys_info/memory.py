# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from pitopcommon.formatting import bytes2human
from components.widgets.common.functions import right_text, title_text, draw_text
from components.widgets.common.values import (
    default_margin_x,
    common_second_line_y,
    common_first_line_y,
    common_third_line_y,
)
from components.widgets.common.base_widgets import BaseSnapshot


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

        title_text(draw, y=default_margin_x, width=width, text="Memory")
        draw_text(draw, xy=(default_margin_x, common_first_line_y), text="Used:")
        draw_text(draw, xy=(default_margin_x,
                            common_second_line_y), text="Phys:")
        draw_text(draw, xy=(default_margin_x, common_third_line_y), text="Swap:")

        right_text(
            draw, common_first_line_y, width, text="{0:0.1f}%".format(
                mem_used_pct)
        )
        right_text(draw, common_second_line_y,
                   width, text=bytes2human(mem.used))
        right_text(draw, common_third_line_y, width,
                   text=bytes2human(swap.used))
