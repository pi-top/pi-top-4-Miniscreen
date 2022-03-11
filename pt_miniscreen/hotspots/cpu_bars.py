import PIL.ImageDraw
from psutil import cpu_percent

from ..state import Speeds
from .base import Hotspot as HotspotBase


class Hotspot(HotspotBase):
    def __init__(self, size, interval=Speeds.DYNAMIC_PAGE_REDRAW.value):
        # Half of the interval time is spent actually collecting the percentages in `Hotspot.render`
        super().__init__(interval=interval / 2, size=size)

    def render(self, image):
        percentages = cpu_percent(interval=self.interval, percpu=True)

        space_between_bars = 4
        num_bars = len(percentages)
        width_cpu = self.size[0] / num_bars if num_bars > 0 else 1
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
