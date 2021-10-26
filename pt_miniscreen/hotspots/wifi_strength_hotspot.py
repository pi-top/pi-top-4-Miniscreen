import PIL.ImageDraw
from pitop.common.sys_info import get_network_strength

from .base import Hotspot as HotspotBase


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval, size, mode)

    def render(self, image):
        wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100

        number_of_bars = 4
        filled_bars = 4
        if wifi_strength <= 0:
            filled_bars = 0
        elif wifi_strength <= 0.25:
            filled_bars = 1
        elif wifi_strength <= 0.5:
            filled_bars = 2
        elif wifi_strength <= 0.75:
            filled_bars = 3

        space_between_bars = 4
        width_cpu = self.size[0] / number_of_bars
        bar_width = width_cpu - space_between_bars

        x = 0
        draw = PIL.ImageDraw.Draw(image)
        for i in range(number_of_bars):
            draw.rectangle(
                (x, self.size[1] * (1 - (i + 1) / number_of_bars))
                + (x + bar_width, self.size[1]),
                "white" if i + 1 <= filled_bars else "black",
                "white",
            )
            x += width_cpu
