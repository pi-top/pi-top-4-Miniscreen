import logging
from threading import Event

from .config import MenuConfigManager
from .event import AppEvents, subscribe
from .state import Speeds

logger = logging.getLogger(__name__)


class MenuManager:
    def __init__(self, size, mode):
        self.is_skipping = False

        self.menus = MenuConfigManager.get_menus_dict(size, mode)

        self.current_menu_id = "hud"
        self.page_has_changed = Event()

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

        def set_menu(new_menu):
            for k, v in new_menu.items():
                self.menus[k] = v
            self.current_menu_id = list(new_menu.keys())[0]

        subscribe(AppEvents.MENU_CHANGE, set_menu)

    @property
    def current_menu(self):
        return self.menus[self.current_menu_id]

    def _go_to_next_menu(self):
        self.current_menu_id = MenuConfigManager.get_next_menu_id(
            self.menus, self.current_menu_id
        )

        if self.current_menu.go_to_first:
            self.current_menu.move_to_page(0)

        self.page_has_changed.set()

    def _go_to_parent_menu(self):
        self.current_menu_id = MenuConfigManager.get_parent_menu_id(
            self.menus, self.current_menu_id
        )

        self.page_has_changed.set()

    def _handle_select_btn(self):
        self.current_menu.current_page.on_select_press()

    def _handle_cancel_btn(self):
        if MenuConfigManager.menu_id_has_parent(self.menus, self.current_menu_id):
            self._go_to_next_menu()
        else:
            self._go_to_parent_menu()

    def _set_current_menu_page_to_previous(self):
        self.current_menu.set_page_to_previous()
        if self.current_menu.needs_to_scroll:
            self.page_has_changed.set()

    def _set_current_menu_page_to_next(self):
        self.current_menu.set_page_to_next()
        if self.current_menu.needs_to_scroll:
            self.page_has_changed.set()

    def update_current_menu_scroll_position(self):
        if not self.current_menu.needs_to_scroll:
            self.is_skipping = False
            return

        self.current_menu.update_scroll_position()

    def wait_until_timeout_or_page_has_changed(self):
        if self.current_menu.needs_to_scroll:
            if self.is_skipping:
                interval = Speeds.SKIP.value
            else:
                interval = Speeds.SCROLL.value
        else:
            interval = self.current_menu.current_page.interval

        self.page_has_changed.wait(interval)
        if self.page_has_changed.is_set():
            self.page_has_changed.clear()
