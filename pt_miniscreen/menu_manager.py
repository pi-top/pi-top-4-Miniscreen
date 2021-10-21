import logging
from threading import Event

from .config import menu_app_config
from .config_factory import ConfigFactory
from .event import AppEvents, subscribe

logger = logging.getLogger(__name__)


class MenuManager:
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, miniscreen, redraw_speed, scroll_speed, skip_speed):
        self.size = miniscreen.size

        self.redraw_speed = redraw_speed
        self.scroll_speed = scroll_speed
        self.skip_speed = skip_speed

        self.is_skipping = False

        menu_factory = ConfigFactory(miniscreen.size, miniscreen.mode, redraw_speed)
        self.menus = {}
        for menu_name, config in menu_app_config.children.items():
            self.menus[menu_name] = menu_factory.get(config)

        self.current_menu_id = "hud"
        self.page_has_changed = Event()

        subscribe(
            AppEvents.UP_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self.set_page_to_previous),
        )
        subscribe(
            AppEvents.DOWN_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self.set_page_to_next),
        )
        subscribe(
            AppEvents.SELECT_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self.handle_select_btn),
        )
        subscribe(
            AppEvents.CANCEL_BUTTON_PRESS,
            lambda callback_handler: callback_handler(self.handle_cancel_btn),
        )

        def set_menu(new_menu):
            self.menus = new_menu
            self.current_menu_id = list(new_menu.keys())[0]

        subscribe(AppEvents.MENU_CHANGE, set_menu)

    @property
    def current_menu(self):
        return self.menus[self.current_menu_id]

    def go_to_next_menu(self):
        keys = list(self.menus.keys())
        current_index = keys.index(self.current_menu_id)
        next_index = 0 if current_index + 1 >= len(self.menus) else current_index + 1
        self.current_menu_id = keys[next_index]

        if self.current_menu.go_to_first:
            self.current_menu.move_to_page(0)
        self.page_has_changed.set()

    def handle_select_btn(self):
        self.current_menu.current_page.on_select_press()

    def handle_cancel_btn(self):
        self.go_to_next_menu()

    def get_page(self, index):
        return self.current_menu.pages[index]

    @property
    def page(self):
        return self.get_page(self.current_menu.page_index)

    def set_page_to_previous(self):
        self.current_menu.set_page_to_previous()
        if self.current_menu.needs_to_scroll:
            self.page_has_changed.set()

    def set_page_to_next(self):
        self.current_menu.set_page_to_next()
        if self.current_menu.needs_to_scroll:
            self.page_has_changed.set()

    def wait_until_timeout_or_page_has_changed(self):
        if self.current_menu.needs_to_scroll:
            if self.is_skipping:
                interval = self.skip_speed
            else:
                interval = self.scroll_speed
        else:
            interval = self.redraw_speed

        self.page_has_changed.wait(interval)
        if self.page_has_changed.is_set():
            self.page_has_changed.clear()

    def update_scroll_position(self):
        if not self.current_menu.needs_to_scroll:
            self.is_skipping = False
            return

        correct_y_pos = self.current_menu.page_index * self.size[1]
        move_down = correct_y_pos > self.current_menu.y_pos

        self.current_menu.y_pos += self.SCROLL_PX_RESOLUTION * (1 if move_down else -1)
