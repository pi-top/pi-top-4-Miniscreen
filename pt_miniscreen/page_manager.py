import logging
from threading import Event

from .config import menu_config
from .event import AppEvents, subscribe

# from .pages import hud, settings

logger = logging.getLogger(__name__)


class PageManager:
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, miniscreen, page_redraw_speed, scroll_speed, skip_speed):
        self._ms = miniscreen

        self.page_redraw_speed = page_redraw_speed
        self.scroll_speed = scroll_speed
        self.skip_speed = skip_speed

        self.is_skipping = False

        self._ms.up_button.when_released = self.set_page_to_previous_page
        self._ms.down_button.when_released = self.set_page_to_next_page
        self._ms.select_button.when_released = self.handle_select_btn
        self._ms.cancel_button.when_released = self.handle_cancel_btn

        hud = menu_config["hud"]["module"]
        settings = menu_config["settings"]["module"]

        self.viewports = {
            "hud": hud.get_viewport(miniscreen, page_redraw_speed),
            "settings": settings.get_viewport(
                miniscreen,
                page_redraw_speed,
            ),
        }

        self.active_viewport_id = "hud"
        self.page_has_changed = Event()

        self.setup_event_triggers()

    @property
    def active_viewport(self):
        return self.viewports[self.active_viewport_id]

    def setup_event_triggers(self):
        def soft_transition_to_last_page(_):
            if self.active_viewport_id != "hud":
                return

            last_page_index = len(self.active_viewport.pages) - 1
            # Only do automatic update if on previous page
            if self.viewports["hud"].page_index == last_page_index - 1:
                self.viewports["hud"].page_index = last_page_index

        subscribe(AppEvents.READY_TO_BE_A_MAKER, soft_transition_to_last_page)

        def hard_transition_to_connect_page(_):
            self.active_viewport_id = "hud"
            self.active_viewport.page_index = len(self.active_viewport.pages) - 2
            self.is_skipping = True

        subscribe(
            AppEvents.USER_SKIPPED_CONNECTION_GUIDE, hard_transition_to_connect_page
        )

    def handle_select_btn(self):
        if self.active_viewport_id == "hud":
            self.set_page_to_next_page()
        else:
            self.active_viewport.current_page.on_select_press()

        self.page_has_changed.set()

    def handle_cancel_btn(self):
        if self.active_viewport_id == "hud":
            self.active_viewport_id = "settings"
            self.active_viewport.move_to_page(0)
        else:
            self.active_viewport_id = "hud"

        self.page_has_changed.set()

    def get_page(self, index):
        return self.active_viewport.pages[index]

    @property
    def page(self):
        return self.get_page(self.active_viewport.page_index)

    @property
    def needs_to_scroll(self):
        y_pos = self.active_viewport.y_pos
        correct_y_pos = self.active_viewport.page_index * self.page.height

        return y_pos != correct_y_pos

    def set_page_to(self, page):
        if self.needs_to_scroll:
            return

        factory = menu_config[self.active_viewport_id]["module"].PageFactory

        new_page = list(factory.pages.keys())[
            list(factory.pages.values()).index(type(page))
        ]

        new_page_index = new_page.value - 1
        if self.active_viewport.page_index == new_page_index:
            logger.debug(
                f"Miniscreen onboarding: Already on page '{new_page.name}' - nothing to do"
            )
            return

        logger.debug(
            f"Page index: {self.active_viewport.page_index} -> {new_page_index}"
        )
        self.active_viewport.page_index = new_page_index
        self.page_has_changed.set()

    def set_page_to_previous_page(self):
        self.set_page_to(self.get_previous_page())

    def set_page_to_next_page(self):
        self.set_page_to(self.get_next_page())

    def get_previous_page(self):
        # Return next page if at top
        if self.active_viewport.page_index == 0:
            return self.get_next_page()

        candidate = self.get_page(self.active_viewport.page_index - 1)
        return candidate if candidate.visible else self.page

    def get_next_page(self):
        # Return current page if at end
        if self.active_viewport.page_index + 1 >= len(self.active_viewport.pages):
            return self.page

        candidate = self.get_page(self.active_viewport.page_index + 1)
        return candidate if candidate.visible else self.page

    def display_current_viewport_image(self):
        self._ms.device.display(self.active_viewport.image)

    def wait_until_timeout_or_page_has_changed(self):
        if self.needs_to_scroll:
            if self.is_skipping:
                interval = self.skip_speed
            else:
                interval = self.scroll_speed
        else:
            interval = self.page_redraw_speed

        self.page_has_changed.wait(interval)
        if self.page_has_changed.is_set():
            self.page_has_changed.clear()

    def update_scroll_position(self):
        if not self.needs_to_scroll:
            self.is_skipping = False
            return

        correct_y_pos = self.active_viewport.page_index * self._ms.size[1]
        move_down = correct_y_pos > self.active_viewport.y_pos

        self.active_viewport.y_pos += self.SCROLL_PX_RESOLUTION * (
            1 if move_down else -1
        )
