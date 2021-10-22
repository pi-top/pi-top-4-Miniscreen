import logging
from threading import Event

from .config import MenuConfigManager
from .event import AppEvents, post_event, subscribe
from .state import Speeds

logger = logging.getLogger(__name__)


class MenuManager:
    def __init__(self, size, mode):
        self.is_skipping = False

        self.menus = MenuConfigManager.get_menus_dict(size, mode)

        self.current_menu_id = "hud"
        self.should_redraw = Event()

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

        self.should_redraw.set()

    def _go_to_child_menu(self):
        new_menu = self.current_menu_page.child_menu
        if not new_menu:
            return

        logger.info("Current menu's page has child menu - setting menu to child")

        for k, v in new_menu.items():
            self.menus[k] = v

        self.current_menu_id = list(new_menu.keys())[0]
        self.should_redraw.set()

    def _go_to_parent_menu(self):
        self.current_menu_id = MenuConfigManager.get_parent_menu_id(
            self.current_menu_id
        )

        self.should_redraw.set()

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
            self.should_redraw.set()

    def _set_current_menu_page_to_next(self):
        self.current_menu.set_page_to_next()
        if self.current_menu.needs_to_scroll:
            self.should_redraw.set()

    def update_current_menu_scroll_position(self):
        if not self.current_menu.needs_to_scroll:
            self.is_skipping = False
            return

        self.current_menu.update_scroll_position()

    def wait_until_timeout_or_should_redraw(self):
        if self.current_menu.needs_to_scroll:
            if self.is_skipping:
                interval = Speeds.SKIP.value
            else:
                interval = Speeds.SCROLL.value
        else:
            interval = self.current_menu_page.interval

        self.should_redraw.wait(interval)
        if self.should_redraw.is_set():
            self.should_redraw.clear()
