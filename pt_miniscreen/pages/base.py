from time import perf_counter

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant


# Based on luma.core hotspots/snapshots
class PageBase:
    def __init__(self, interval=1, size=(128, 64), mode="1"):
        self.interval = interval
        self.size = size
        self.mode = mode

        self.last_updated = -self.interval
        self.invert = False
        self.width = size[0]
        self.height = size[1]
        self.visible = True
        self.font_size = 14
        self.wrap = True

    def should_redraw(self):
        """Only requests a redraw after ``interval`` seconds have elapsed."""
        return perf_counter() - self.last_updated > self.interval

    def paste_into(self, image, xy):
        im = Image.new(image.mode, self.size)
        self.render(im)
        if self.invert:
            im = MiniscreenAssistant(self.mode, self.size).invert(im)
        image.paste(im, xy)
        del im
        self.last_updated = perf_counter()

    def render(self, image):
        raise NotImplementedError
