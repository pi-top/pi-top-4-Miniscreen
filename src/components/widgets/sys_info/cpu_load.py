# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common.functions import get_image_file
from components.widgets.common.image_component import ImageComponent


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.image = ImageComponent(
            image_path=get_image_file("sys_info/cpu_page.gif"), loop=False
        )

    def render(self, draw, width, height):
        self.image.render(draw)
        percentages = psutil.cpu_percent(interval=None, percpu=True)

        top_margin = 10
        bottom_margin = 10

        bar_height = height - top_margin - bottom_margin
        width_cpu = (width / 2) / len(percentages)
        bar_width = 10
        bar_margin = 10

        x = bar_margin

        for cpu in percentages:
            cpu_height = bar_height * (cpu / 100.0)
            y2 = height - bottom_margin
            vertical_bar(
                draw,
                width - x,
                y2 - bar_height - 1,
                width - x - bar_width,
                y2,
                y2 - cpu_height,
            )

            x += width_cpu
