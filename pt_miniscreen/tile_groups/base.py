import logging
from threading import Event
from time import sleep

import PIL.Image

from .event import AppEvents, post_event, subscribe
from .state import Speeds

logger = logging.getLogger(__name__)


class TileGroup:
    def __init__(
        self,
        size,
        menu_tile,
        title_bar_tile=None,
    ):
        self.size = size
        self.menu_tile = menu_tile

        self.title_bar_tile = title_bar_tile

        self.should_redraw_event = Event()
        self._active = False

        subscribe(
            AppEvents.UPDATE_DISPLAYED_IMAGE,
            lambda _: self.should_redraw_event.set(),
        )

    def stop(self):
        if self.title_bar_tile:
            self.title_bar_tile.stop()
        self.menu_tile.stop()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, is_active):
        self._active = is_active
        self.menu_tile.active = self.active
        if self.title_bar_tile:
            self.title_bar_tile.active = self.active

    @property
    def image(self):
        self.menu_tile.update_scroll_position()

        im = PIL.Image.new("1", self.size)

        def paste_tile_into_image(tile, image):
            box = (
                tile.pos[0],
                tile.pos[1],
                tile.pos[0] + tile.size[0],
                tile.pos[1] + tile.size[1],
            )
            logger.debug(
                f"Pasting tile '{tile}' (size: {tile.size})"
                f" into image '{image}' (size: {image.size})"
                f", box: {box}"
            )
            image.paste(tile.image, box)

        if self.title_bar_tile:
            paste_tile_into_image(self.title_bar_tile, im)

        paste_tile_into_image(self.menu_tile, im)

        return im

    def wait_until_should_redraw(self):
        if self.menu_tile.needs_to_scroll:
            sleep(Speeds.SCROLL.value)
        else:
            self.should_redraw_event.wait()

        if self.should_redraw_event.is_set():
            self.should_redraw_event.clear()

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        if self.menu_tile._current_page.child_menu:
            self.menu_tile._go_to_child_menu()
            return True
        elif False:
            post_event(AppEvents.BUTTON_ACTION_START)
            return True
        else:
            return False

    def handle_cancel_btn(self):
        return False

    def handle_up_btn(self):
        self.menu_tile.set_page_to_previous()

        if self.menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

        return True

    def handle_down_btn(self):
        self.menu_tile.set_page_to_next()

        if self.menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

        return True
