import PIL.Image
import PIL.ImageDraw
import psutil

from ...utils import get_image_file_path
from ..base import PageBase


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.cpu_image = PIL.Image.open(get_image_file_path("sys_info/cpu.png"))

    def render(self, image):
        draw = PIL.ImageDraw.Draw(image)
        draw.bitmap(
            xy=(0, 0),
            bitmap=self.cpu_image.convert(self.mode),
            fill="white",
        )

        percentages = psutil.cpu_percent(interval=None, percpu=True)

        top_margin = 10
        bottom_margin = 10

        bar_height = self.size[1] - top_margin - bottom_margin
        width_cpu = (self.size[0] / 2) / len(percentages)
        bar_width = 10
        bar_margin = 10

        x = bar_margin

        for cpu in percentages:
            cpu_height = bar_height * (cpu / 100.0)
            y2 = self.size[1] - bottom_margin
            vertical_bar(
                draw,
                self.size[0] - x,
                y2 - bar_height - 1,
                self.size[0] - x - bar_width,
                y2,
                y2 - cpu_height,
            )

            x += width_cpu
