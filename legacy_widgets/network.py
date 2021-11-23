# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from pitop.common.formatting import bytes2human

from ..widgets.common import (
    BaseSnapshot,
    common_first_line_y,
    common_second_line_y,
    common_third_line_y,
    default_margin_x,
    default_margin_y,
    draw_text,
    right_text,
    title_text,
)


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.interface = data.get("interface")

    def render(self, draw, width, height):
        title_text(draw, default_margin_y, width, text="Net:{0}".format(self.interface))
        try:
            address = psutil.net_if_addrs()[self.interface][0].address
            counters = psutil.net_io_counters(pernic=True)[self.interface]

            draw_text(draw, xy=(default_margin_x, common_first_line_y), text=address)
            draw_text(draw, xy=(default_margin_x, common_second_line_y), text="Rx:")
            draw_text(draw, xy=(default_margin_x, common_third_line_y), text="Tx:")

            right_text(
                draw, common_second_line_y, width, text=bytes2human(counters.bytes_recv)
            )
            right_text(
                draw, common_third_line_y, width, text=bytes2human(counters.bytes_sent)
            )
        except Exception:
            draw_text(draw, xy=(default_margin_x, common_first_line_y), text="n/a")
