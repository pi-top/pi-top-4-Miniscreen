from time import perf_counter

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant


# Based on luma.core hotspots/snapshots
class HotspotBase:
    def __init__(self, interval, size, mode):
        self.interval = interval
        self.size = size
        self.mode = mode

        self.last_updated = -self.interval
        self.invert = False
        self.width = size[0]
        self.height = size[1]
        # self.visible = True
        # self.font_size = 14
        # self.wrap = True

    def should_redraw(self):
        """Only requests a redraw after ``interval`` seconds have elapsed."""
        return perf_counter() - self.last_updated > self.interval

    def paste_into(self, image, xy):
        hotspot_image = Image.new(image.mode, self.size)
        self.render(hotspot_image)
        if self.invert:
            hotspot_image = MiniscreenAssistant(self.mode, self.size).invert(
                hotspot_image
            )
        mask = hotspot_image
        image.paste(hotspot_image, xy, mask)
        del hotspot_image
        self.last_updated = perf_counter()

    def render(self, image):
        raise NotImplementedError
