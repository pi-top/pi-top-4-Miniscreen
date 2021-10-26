import PIL.ImageDraw
import psutil

from .base import Hotspot as HotspotBase


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval, size, mode)

    def render(self, image):
        percentages = psutil.cpu_percent(interval=None, percpu=True)

        space_between_bars = 4
        width_cpu = self.size[0] / len(percentages)
        bar_width = width_cpu - space_between_bars

        x = 0
        draw = PIL.ImageDraw.Draw(image)
        y_margin = 1
        for cpu in percentages:
            cpu_height = self.size[1] * cpu / 100.0
            draw.rectangle(
                (x, 0) + (x + bar_width, self.size[1] - y_margin), "black", "white"
            )
            draw.rectangle(
                (x, self.size[1] - y_margin - cpu_height)
                + (x + bar_width, self.size[1] - y_margin),
                "white",
                "white",
            )
            x += width_cpu
