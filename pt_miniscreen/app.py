import logging
from os import environ
from threading import Event, Timer

from pitop import Pitop

from .core import App as BaseApp
from .root import RootComponent

logger = logging.getLogger(__name__)


class App(BaseApp):
    DIMMING_TIMEOUT = 20
    SCREENSAVER_TIMEOUT = 20

    def __init__(self):
        logger.debug("Setting ENV VAR to use miniscreen as system...")
        environ["PT_MINISCREEN_SYSTEM"] = "1"

        logger.debug("Initializing miniscreen...")
        miniscreen = Pitop().miniscreen

        self.user_gave_back_control_event = Event()

        def set_is_user_controlled(user_has_control) -> None:
            if not user_has_control:
                self.user_gave_back_control_event.set()

            logger.info(
                f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
            )

        miniscreen.when_user_controlled = lambda: set_is_user_controlled(True)
        miniscreen.when_system_controlled = lambda: set_is_user_controlled(False)
        miniscreen.select_button.when_released = self.handle_select_button_release
        miniscreen.cancel_button.when_released = self.handle_cancel_button_release
        miniscreen.up_button.when_released = self.handle_up_button_release
        miniscreen.down_button.when_released = self.handle_down_button_release

        self.timer = None
        self._contrast = 255
        self.configure_timing_events()

        logger.error("Initialising app...")
        super().__init__(miniscreen, Root=RootComponent)

    def handle_inactive_state(self) -> bool:
        should_handle_button_press = True

        if self.miniscreen.get_contrast() == 0:
            self.miniscreen.contrast(255)
            self.configure_timing_events()
            should_handle_button_press = False

        if self.root.is_screensaver_running:
            self.root.stop_screensaver()
            should_handle_button_press = False

        if should_handle_button_press:
            self.configure_timing_events()

        return should_handle_button_press

    def handle_select_button_release(self):
        should_handle_button_press = self.handle_inactive_state()
        if not should_handle_button_press:
            return

        if self.root.can_enter_menu:
            return self.root.enter_menu()

        if self.root.can_perform_action:
            return self.root.perform_action()

    def handle_cancel_button_release(self):
        should_handle_button_press = self.handle_inactive_state()
        if not should_handle_button_press:
            return

        self.root.exit_menu()

    def handle_up_button_release(self):
        should_handle_button_press = self.handle_inactive_state()
        if not should_handle_button_press:
            return

        self.root.scroll_up()

    def handle_down_button_release(self):
        should_handle_button_press = self.handle_inactive_state()
        if not should_handle_button_press:
            return

        self.root.scroll_down()

    def display(self):
        if self.user_has_control:
            logger.info("User has control. Waiting for user to give control back...")
            self.user_gave_back_control_event.wait()
            self.user_gave_back_control_event.clear()
            self.display()

        super().display()

    @property
    def user_has_control(self) -> bool:
        return self.miniscreen.is_active

    def configure_timing_events(self) -> None:
        if self.timer and isinstance(self.timer, Timer):
            self.timer.cancel()

        def dim_and_start_screensaver_timer():
            self.miniscreen.contrast(0)
            self.timer = Timer(self.SCREENSAVER_TIMEOUT, self.root.start_screensaver)
            self.timer.start()

        self.timer = Timer(self.DIMMING_TIMEOUT, dim_and_start_screensaver_timer)
        self.timer.start()
