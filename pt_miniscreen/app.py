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

        self.screensaver_timer = None
        self.dimming_timer = None
        self.start_dimming_timer()

        logger.debug("Initialising app...")
        super().__init__(miniscreen, Root=RootComponent)

    def on_button_press(self):
        if self.dimmed:
            self.miniscreen.contrast(255)

        self.restart_dimming_timer()

    def handle_select_button_release(self):
        self.on_button_press()

        if self.root.is_screensaver_running:
            return self.root.stop_screensaver()

        if self.root.can_enter_menu:
            return self.root.enter_menu()

        if self.root.can_perform_action:
            return self.root.perform_action()

    def handle_cancel_button_release(self):
        self.on_button_press()

        if self.root.is_screensaver_running:
            return self.root.stop_screensaver()

        self.root.exit_menu()

    def handle_up_button_release(self):
        self.on_button_press()

        if self.root.is_screensaver_running:
            return self.root.stop_screensaver()

        self.root.scroll_up()

    def handle_down_button_release(self):
        self.on_button_press()

        if self.root.is_screensaver_running:
            return self.root.stop_screensaver()

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

    def start_screensaver_timer(self):
        self.screensaver_timer = Timer(
            self.SCREENSAVER_TIMEOUT, self.root.start_screensaver
        )
        self.screensaver_timer.start()

    def start_dimming_timer(self):
        def dim_and_start_screensaver_timer():
            self.miniscreen.contrast(0)
            self.start_screensaver_timer()

        self.dimming_timer = Timer(
            self.DIMMING_TIMEOUT, dim_and_start_screensaver_timer
        )
        self.dimming_timer.start()

    def restart_dimming_timer(self):
        for timer in (self.dimming_timer, self.screensaver_timer):
            if timer and isinstance(timer, Timer):
                timer.cancel()

        self.start_dimming_timer()

    @property
    def dimmed(self):
        return (
            self.screensaver_timer
            and self.screensaver_timer.is_alive()
            or self.root.is_screensaver_running
        )
