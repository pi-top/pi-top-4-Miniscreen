import logging
from threading import Event
from time import sleep

import PIL.Image

from ..event import AppEvents, subscribe
from ..state import Speeds

logger = logging.getLogger(__name__)


class TileGroup:
    def __init__(
        self,
        size,
        menu_tile,
        title_bar_tile=None,
    ):
        self.size = size

        self.menu_tiles = [menu_tile]

        self.title_bar_tile = title_bar_tile

        self.should_redraw_event = Event()
        self._active = False

        subscribe(
            AppEvents.UPDATE_DISPLAYED_IMAGE,
            lambda _: self.should_redraw_event.set(),
        )

        def add_menu_tile(menu_tile):
            if not self.active:
                return
            self.current_menu_tile.active = False
            self.menu_tiles.append(menu_tile)
            self.current_menu_tile.active = True

        subscribe(
            AppEvents.GO_TO_CHILD_MENU,
            add_menu_tile,
        )

        def remove_menu_tile(menu_tile):
            if not self.active or len(self.menu_tiles) == 1:
                return
            self.menu_tiles.remove(menu_tile)
            self.current_menu_tile.active = True

        subscribe(
            AppEvents.GO_TO_PARENT_MENU,
            remove_menu_tile,
        )

    @property
    def current_menu_tile(self):
        return self.menu_tiles[-1]

    def stop(self):
        if self.title_bar_tile:
            self.title_bar_tile.stop()
        self.current_menu_tile.stop()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, is_active):
        self._active = is_active
        self.current_menu_tile.active = self.active
        if self.title_bar_tile:
            self.title_bar_tile.active = self.active

    @property
    def image(self):
        im = PIL.Image.new("1", self.size)

        def paste_tile_into_image(tile, image):
            box = (
                tile.pos[0],
                tile.pos[1],
                # TODO: fails when moving from child back to parent
                # tile.pos[0] + tile.size[0],
                # tile.pos[1] + tile.size[1],
            )
            logger.debug(
                f"Pasting tile '{tile}' (size: {tile.size})"
                f" into image '{image}' (size: {image.size})"
                f", box: {box}"
            )
            image.paste(tile.image, box)

        if self.title_bar_tile:
            paste_tile_into_image(self.title_bar_tile, im)

        paste_tile_into_image(self.current_menu_tile, im)

        return im

    def wait_until_should_redraw(self):
        # TODO: time event-based redraw event
        #
        # i.e. `self.should_redraw_event.set()` every `Speeds.SCROLL.value`` seconds
        # and other redraw events are ignored until scrolling has completed
        # (to ensure that scrolling generators work correctly)
        if self.current_menu_tile.needs_to_scroll:
            sleep(Speeds.SCROLL.value)
        else:
            self.should_redraw_event.wait()

        if self.should_redraw_event.is_set():
            self.should_redraw_event.clear()

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        return self.current_menu_tile.handle_select_btn()

    def handle_cancel_btn(self):
        return self.current_menu_tile.handle_cancel_btn()

    def handle_up_btn(self):
        return self.current_menu_tile.handle_up_btn()

    def handle_down_btn(self):
        return self.current_menu_tile.handle_down_btn()
