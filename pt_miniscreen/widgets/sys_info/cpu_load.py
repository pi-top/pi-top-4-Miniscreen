# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from .widgets.common import BaseSnapshot, get_image_file_path, ImageComponent


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.image = ImageComponent(
            device_mode=mode,
            width=width,
            height=height,
            image_path=get_image_file_path("sys_info/cpu.png"),
            loop=False,
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
