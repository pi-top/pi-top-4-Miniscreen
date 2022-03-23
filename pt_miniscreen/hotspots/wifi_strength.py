import PIL.ImageDraw
from pitop.common.sys_info import get_network_strength

from pt_miniscreen.core.hotspot import Hotspot


def get_wifi_strength():
    return int(get_network_strength("wlan0")[:-1]) / 100


class WifiStrength(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, initial_state={"wifi_strength": get_wifi_strength()})

        self.create_interval(self.update_wifi_strength)

    def update_wifi_strength(self):
        self.state.update({"wifi_strength": get_wifi_strength()})

    def render(self, image):
        wifi_strength = self.state["wifi_strength"]

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
        right_padding = int(image.width * 0.16)
        width_cpu = (image.width - right_padding) / number_of_bars
        bar_width = width_cpu - space_between_bars

        x = 0
        draw = PIL.ImageDraw.Draw(image)
        for i in range(number_of_bars):
            draw.rectangle(
                (x, image.height * (1 - (i + 1) / number_of_bars))
                + (x + bar_width, image.height - 1),
                "white" if i + 1 <= filled_bars else "black",
                "white",
            )
            x += width_cpu

        return image
