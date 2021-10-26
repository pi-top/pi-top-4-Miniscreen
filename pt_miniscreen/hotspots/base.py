from time import perf_counter

from PIL import Image, ImageOps
from pitop.miniscreen.oled.assistant import MiniscreenAssistant


# Based on luma.core hotspots/snapshots
class HotspotBase:
    def __init__(self, interval, size, mode):
        self.interval = interval
        self.size = size
        self.mode = mode

        self.draw_white = True
        self.draw_black = False

        self.last_updated = -self.interval
        self.invert = False
        self.width = size[0]
        self.height = size[1]

    def should_redraw(self):
        if not self.draw_white and not self.draw_black:
            return False

        """Only requests a redraw after ``interval`` seconds have elapsed."""
        return perf_counter() - self.last_updated > self.interval

    def paste_into(self, image, xy):
        if not self.draw_white and not self.draw_black:
            return

        hotspot_image = Image.new(image.mode, self.size)
        self.render(hotspot_image)

        if self.invert:
            hotspot_image = MiniscreenAssistant(self.mode, self.size).invert(
                hotspot_image
            )

        mask = None
        if self.draw_white and not self.draw_black:
            mask = hotspot_image

        elif not self.draw_white and self.draw_black:
            mask = ImageOps.invert(hotspot_image)

        image.paste(hotspot_image, xy, mask)

        del hotspot_image
        self.last_updated = perf_counter()

    def render(self, image):
        raise NotImplementedError
