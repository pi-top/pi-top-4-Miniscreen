import logging
from threading import Event

import PIL.Image

from .config import MenuConfigManager
from .event import AppEvents, post_event, subscribe

logger = logging.getLogger(__name__)


class MenuManager:
    def __init__(self, size, mode):
        self.size = size
        self.mode = mode
        self.is_skipping = False

        self.title_bar = MenuConfigManager.get_title_bar(size)
        self.menus = MenuConfigManager.get_menus_dict(size, mode)
        self.should_redraw_event = Event()

        def update_current_menu_height(height):
            new_height = self.size[1] - self.title_bar.window_size[1]
            if self.current_menu.window_height != new_height:
                logger.debug(f"Updating Menu height to {new_height}")
                self.current_menu.window_height = new_height

        subscribe(AppEvents.TITLE_BAR_HEIGHT_SET, update_current_menu_height)

        self.current_menu_id = list(self.menus.keys())[0]

        subscribe(
            AppEvents.UP_BUTTON_PRESS,
            lambda callback_handler: callback_handler(
                self._set_current_menu_page_to_previous
            ),
        )
        subscribe(
            AppEvents.DOWN_BUTTON_PRESS,
            lambda callback_handler: callback_handler(
                self._set_current_menu_page_to_next
            ),
        )
        subscribe(
            AppEvents.SELECT_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self._handle_select_btn),
        )
        subscribe(
            AppEvents.CANCEL_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self._handle_cancel_btn),
        )

    @property
    def image(self):
        im = PIL.Image.new(self.mode, self.size)
        title_bar_height = 0
        if self.title_bar is not None and self.title_bar.should_draw():
            title_bar_height = self.title_bar.viewport_size[1]
            title_bar_im = self.title_bar.image
            im.paste(title_bar_im, (0, 0) + (self.size[0], title_bar_height))
        im.paste(self.current_menu.image, (0, title_bar_height))
        return im

    @property
    def current_menu_id(self):
        return self._current_menu_id

    @current_menu_id.setter
    def current_menu_id(self, menu_id):
        self._current_menu_id = menu_id
        self.title_bar.behaviour = self.current_menu.title_bar
        self.should_redraw_event.set()

    @property
    def current_menu(self):
        return self.menus[self.current_menu_id]

    @property
    def current_menu_page(self):
        return self.current_menu.current_page

    def _go_to_next_menu(self):
        self.current_menu_id = MenuConfigManager.get_next_menu_id(
            self.menus, self.current_menu_id
        )
        if self.current_menu.parent_goes_to_first_page:
            self.current_menu.move_to_page(0)
        self.should_redraw_event.set()

    def _go_to_child_menu(self):
        new_menu = self.current_menu_page.child_menu
        if not new_menu:
            return

        logger.info("Current menu's page has child menu - setting menu to child")

        for k, v in new_menu.items():
            self.menus[k] = v
        self.current_menu_id = list(new_menu.keys())[0]

        if self.current_menu.parent_goes_to_first_page:
            self.current_menu.move_to_page(0)

        self.should_redraw_event.set()

    def _go_to_parent_menu(self):

        self.current_menu_id = MenuConfigManager.get_parent_menu_id(
            self.current_menu_id
        )

        self.should_redraw_event.set()

    def _handle_select_btn(self):
        if self.current_menu_page.child_menu:
            self._go_to_child_menu()
        else:
            post_event(AppEvents.BUTTON_ACTION_START)
            self.current_menu_page.on_select_press()

    def _handle_cancel_btn(self):
        if MenuConfigManager.menu_id_has_parent(self.menus, self.current_menu_id):
            self._go_to_parent_menu()
        else:
            self._go_to_next_menu()

    def _set_current_menu_page_to_previous(self):
        self.current_menu.set_page_to_previous()
        if self.current_menu.needs_to_scroll:
            self.should_redraw_event.set()

    def _set_current_menu_page_to_next(self):
        self.current_menu.set_page_to_next()
        if self.current_menu.needs_to_scroll:
            self.should_redraw_event.set()

    def update_current_menu_scroll_position(self):
        if not self.current_menu.needs_to_scroll:
            self.is_skipping = False
            return

        self.current_menu.update_scroll_position()

    def wait_until_timeout_or_should_redraw_event(self, timeout):
        self.should_redraw_event.wait(timeout)
        if self.should_redraw_event.is_set():
            self.should_redraw_event.clear()
