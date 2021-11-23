import logging
from threading import Event
from time import sleep

import PIL.Image

from .pages.overlay.title_bar import TitleBar
from .state import Speeds
from .tiles.menu import MenuTile

# from imgcat import imgcat


logger = logging.getLogger(__name__)


class TileGroup:
    def __init__(self, size, mode):
        self.size = size
        self.mode = mode

        # TODO: title bar needs to have its properties set
        self.title_bar_tile = TitleBar(size=(0, 0))

        # TODO: menus need to know about their children!
        self.menu_tile = MenuTile(
            size=self.size,
            mode=self.mode,
        )

        self.should_redraw_event = Event()
        self._active = False

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, is_active):
        self._active = is_active
        self.menu_tile.active = self.active
        self.title_bar_tile.active = self.active

    @property
    def image(self):
        self.menu_tile.update_scroll_position()

        im = PIL.Image.new(self.mode, self.size)

        if self.title_bar_tile.size != (0, 0):
            im.paste(self.title_bar_tile.image, (0, 0))

        # Offset menu tile image by height of title bar
        im.paste(self.menu_tile.image, (0, self.title_bar_tile.size[1]))

        # logger.debug(f"im.size: {im.size}")
        # logger.debug(f"title_bar_height: {title_bar_height}")
        # logger.debug(f"self.menu_tile: {self.menu_tile}")
        # logger.debug(f"self.menu_tile.image: {self.menu_tile.image}")

        # imgcat(self.menu_tile.image)

        return im

    def wait_until_should_redraw(self):
        if self.menu_tile.needs_to_scroll:
            sleep(Speeds.SCROLL.value)
        else:
            self.should_redraw_event.wait()

        if self.should_redraw_event.is_set():
            self.should_redraw_event.clear()
