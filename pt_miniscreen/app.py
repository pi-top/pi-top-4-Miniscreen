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
        miniscreen.select_button.when_released = self.create_button_handler(
            self.handle_select_button_release
        )
        miniscreen.cancel_button.when_released = self.create_button_handler(
            self.handle_cancel_button_release
        )
        miniscreen.up_button.when_released = self.create_button_handler(
            self.handle_up_button_release
        )
        miniscreen.down_button.when_released = self.create_button_handler(
            self.handle_down_button_release
        )

        self.dimmed = False
        self.screensaver_timer = None
        self.dimming_timer = None
        self.start_dimming_timer()

        logger.debug("Initialising app...")
        super().__init__(miniscreen, Root=RootComponent)

    def brighten(self):
        self.miniscreen.contrast(255)
        self.dimmed = False

    def dim(self):
        self.miniscreen.contrast(0)
        self.dimmed = True

    def create_button_handler(self, func):
        def handler():
            if self.user_has_control:
                logger.debug("User has control of miniscreen, omitting button press...")
                return

            self.restart_dimming_timer()

            if self.root.is_screensaver_running:
                self.root.stop_screensaver()
                self.brighten()
                return

            if callable(func):
                func()

            if self.dimmed:
                self.brighten()

        return handler

    def handle_select_button_release(self):
        if self.root.can_enter_menu:
            return self.root.enter_menu()

        if self.root.can_perform_action:
            return self.root.perform_action()

    def handle_cancel_button_release(self):
        self.root.exit_menu()

    def handle_up_button_release(self):
        self.root.scroll_up()

    def handle_down_button_release(self):
        self.root.scroll_down()

    def display(self):
        def restore_miniscreen():
            try:
                self.miniscreen.reset()
            except RuntimeError as e:
                logger.error(f"Error resetting miniscreen: {e}")

            if self.root.is_screensaver_running:
                self.root.stop_screensaver()
            self.brighten()
            self.restart_dimming_timer()

        if self.user_has_control:
            self.stop_timers()
            logger.info("User has control. Waiting for user to give control back...")
            self.user_gave_back_control_event.wait()
            self.user_gave_back_control_event.clear()
            restore_miniscreen()

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
            self.dim()
            self.start_screensaver_timer()

        self.dimming_timer = Timer(
            self.DIMMING_TIMEOUT, dim_and_start_screensaver_timer
        )
        self.dimming_timer.start()

    def restart_dimming_timer(self):
        self.stop_timers()
        self.start_dimming_timer()

    def stop_timers(self):
        for timer in (self.dimming_timer, self.screensaver_timer):
            if timer and isinstance(timer, Timer):
                timer.cancel()
