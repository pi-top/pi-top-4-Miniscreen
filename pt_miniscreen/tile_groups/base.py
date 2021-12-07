import logging
from threading import Event

import PIL.Image

from ..event import AppEvent, subscribe
from ..types import Coordinate

logger = logging.getLogger(__name__)


class TileGroup:
    def __init__(
        self,
        size: Coordinate,
        menu_tile,
        title_bar_tile=None,
    ) -> None:
        self.size = size

        self._current_menu_tile = menu_tile

        self.title_bar_tile = title_bar_tile

        self.should_redraw_event = Event()
        self._active = False

        subscribe(
            AppEvent.UPDATE_DISPLAYED_IMAGE,
            lambda: self.should_redraw_event.set(),
        )

    @property
    def current_menu_tile(self):
        return self._current_menu_tile

    def stop(self) -> None:
        if self.title_bar_tile:
            self.title_bar_tile.stop()
        self.current_menu_tile.stop()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, is_active: bool) -> None:
        self._active = is_active
        self.current_menu_tile.active = self.active
        if self.title_bar_tile:
            self.title_bar_tile.active = self.active

    @property
    def image(self) -> PIL.Image.Image:
        im = PIL.Image.new("1", self.size)

        def paste_tile_into_image(tile, image):
            logger.debug(
                f"Pasting tile '{tile}' (size: {tile.size})"
                f" into image '{image}' (size: {image.size})"
                f", pos: {tile.pos}"
            )
            image.paste(tile.image, tile.pos)

        # Paste images without mask
        if self.title_bar_tile:
            paste_tile_into_image(self.title_bar_tile, im)

        paste_tile_into_image(self.current_menu_tile, im)

        return im

    def wait_until_should_redraw(self) -> None:
        self.should_redraw_event.wait()

        if self.should_redraw_event.is_set():
            self.should_redraw_event.clear()

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self) -> bool:
        return self.current_menu_tile.handle_select_btn()

    def handle_cancel_btn(self) -> bool:
        return self.current_menu_tile.handle_cancel_btn()

    def handle_up_btn(self) -> bool:
        return self.current_menu_tile.handle_up_btn()

    def handle_down_btn(self) -> bool:
        return self.current_menu_tile.handle_down_btn()
