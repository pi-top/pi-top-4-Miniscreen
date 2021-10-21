from time import perf_counter

from PIL import Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..config_factory import ConfigFactory
from ..event import AppEvents, post_event


# Based on luma.core hotspots/snapshots
class PageBase:
    def __init__(self, interval, size, mode, config):
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

        menu_factory = ConfigFactory(size, mode, interval)
        self.child_menu = {}
        if config.child_menu:
            for name, config in config.child_menu.items():
                self.child_menu[name] = menu_factory.get(config)

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

    def on_select_press(self):
        if self.child_menu:
            post_event(AppEvents.MENU_CHANGE, self.child_menu)
