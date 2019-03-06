# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.formatting import bytes2human
import psutil
from components.widgets.common_functions import right_text, title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.interface = data.get("interface")

    def render(self, draw, width, height):
        margin = 3
        title_text(draw, margin, width, text="Net:{0}".format(self.interface))
        try:
            address = psutil.net_if_addrs()[self.interface][0].address
            counters = psutil.net_io_counters(pernic=True)[self.interface]

            draw_text(draw, xy=(margin, 20), text=address)
            draw_text(draw, xy=(margin, 35), text="Rx:")
            draw_text(draw, xy=(margin, 50), text="Tx:")

            right_text(draw, 35, width, margin, text=bytes2human(counters.bytes_recv))
            right_text(draw, 50, width, margin, text=bytes2human(counters.bytes_sent))
        except:
            draw_text(draw, xy=(margin, 20), text="n/a")
