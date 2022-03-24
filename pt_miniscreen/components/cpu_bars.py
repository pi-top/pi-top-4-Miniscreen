import logging

import PIL.ImageDraw
from psutil import cpu_percent

from pt_miniscreen.core.component import Component

logger = logging.getLogger(__name__)


class CPUBars(Component):
    def __init__(self, **kwargs):
        percentages = cpu_percent(percpu=True)
        super().__init__(**kwargs, initial_state={"percentages": percentages})
        self.create_interval(self.update_percentages)

    def update_percentages(self):
        percentages = cpu_percent(interval=0.5, percpu=True)
        self.state.update({"percentages": percentages})

    def render(self, image):
        percentages = self.state["percentages"]
        space_between_bars = 4
        num_bars = len(percentages)
        width_cpu = image.width / num_bars if num_bars > 0 else 1
        bar_width = width_cpu - space_between_bars

        x = 0
        draw = PIL.ImageDraw.Draw(image)
        y_margin = 1
        for cpu in percentages:
            cpu_height = image.height * cpu / 100.0
            draw.rectangle(
                (x, 0) + (x + bar_width, image.height - y_margin), "black", "white"
            )
            draw.rectangle(
                (x, image.height - y_margin - cpu_height)
                + (x + bar_width, image.height - y_margin),
                "white",
                "white",
            )
            x += width_cpu

        return image
