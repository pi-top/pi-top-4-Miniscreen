# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        percentages = psutil.cpu_percent(interval=None, percpu=True)

        top_margin = 3
        bottom_margin = 3
        title_text(draw, top_margin, width, "CPU Load")

        bar_height = height - 15 - top_margin - bottom_margin
        width_cpu = width / len(percentages)
        bar_width = 0.5 * width_cpu
        bar_margin = (width_cpu - bar_width) / 2

        x = bar_margin

        for cpu in percentages:
            cpu_height = bar_height * (cpu / 100.0)
            y2 = height - bottom_margin
            vertical_bar(
                draw, x, y2 - bar_height - 1, x + bar_width, y2, y2 - cpu_height
            )

            x += width_cpu
