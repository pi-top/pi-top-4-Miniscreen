import logging
from threading import Event

from .config import menu_config
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
        for menu_name, config in menu_config.items():
            self.menus[menu_name] = menu_factory.get(config)

        self.current_menu_id = "hud"
        self.page_has_changed = Event()

        self.setup_event_triggers()

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

    @property
    def current_menu(self):
        return self.menus[self.current_menu_id]

    def setup_event_triggers(self):
        def soft_transition_to_last_page(_):
            if self.current_menu_id != "hud":
                return

            last_page_index = len(self.current_menu.pages) - 1
            # Only do automatic update if on previous page
            if self.menus["hud"].page_index == last_page_index - 1:
                self.menus["hud"].page_index = last_page_index

        subscribe(AppEvents.READY_TO_BE_A_MAKER, soft_transition_to_last_page)

        def hard_transition_to_connect_page(_):
            self.current_menu_id = "hud"
            self.current_menu.page_index = len(self.current_menu.pages) - 2
            self.is_skipping = True

        subscribe(
            AppEvents.USER_SKIPPED_CONNECTION_GUIDE, hard_transition_to_connect_page
        )

    def handle_select_btn(self):
        if self.current_menu_id == "hud":
            self.set_page_to_next()
        else:
            self.current_menu.current_page.on_select_press()

        self.page_has_changed.set()

    def handle_cancel_btn(self):
        if self.current_menu_id == "hud":
            self.current_menu_id = "settings"
            self.current_menu.move_to_page(0)
        else:
            self.current_menu_id = "hud"

        self.page_has_changed.set()

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
