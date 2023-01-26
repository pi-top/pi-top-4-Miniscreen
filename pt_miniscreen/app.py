import logging
import traceback
from os import environ
from threading import Timer
from pt_miniscreen.utils import ButtonEvents

from pitop.system.pitop import Pitop

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
        self.miniscreen = Pitop().miniscreen

        logger.debug("Initialising app...")

        # display should be `miniscreen.display_image` but that method attempts to
        # import opencv when it's called. We can catch the raised error but cannot
        # prevent the module search. This produces overhead when display is called
        # frequently, which is expected. It's worth noting the import is not cached
        # since the module was not found so the search happens every import attempt
        super().__init__(
            display=self.miniscreen.device.display,
            size=self.miniscreen.size,
            Root=RootComponent,
        )

    def start(self):
        super().start()

        def set_is_user_controlled(user_has_control) -> None:
            if user_has_control:
                self.stop_timers()
                if self.root.is_project_page:
                    self.root.project_uses_miniscreen(True)
            else:
                self.restore_miniscreen()

            logger.info(
                f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
            )

        self.miniscreen.when_user_controlled = lambda: set_is_user_controlled(True)
        self.miniscreen.when_system_controlled = lambda: set_is_user_controlled(False)
        self.miniscreen.select_button.when_released = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.SELECT_RELEASE)
        )
        self.miniscreen.cancel_button.when_released = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.CANCEL_RELEASE)
        )
        self.miniscreen.up_button.when_released = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.UP_RELEASE)
        )
        self.miniscreen.down_button.when_released = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.DOWN_RELEASE)
        )
        self.miniscreen.up_button.when_pressed = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.UP_PRESS)
        )
        self.miniscreen.down_button.when_pressed = self.create_button_handler(
            lambda: self.root.handle_button(ButtonEvents.DOWN_PRESS)
        )

        self.dimmed = False
        self.screensaver_timer = None
        self.dimming_timer = None
        self.start_dimming_timer()

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

            try:
                if self.root.is_screensaver_running:
                    self.root.stop_screensaver()
                    self.brighten()
                    return

                if callable(func):
                    func()

            except Exception as e:
                logger.error("Error in button handler: " + str(e))
                traceback.print_exc()
                self.stop(e)

            if self.dimmed:
                self.brighten()

        return handler

    def restore_miniscreen(self):
        try:
            self.miniscreen.reset()
        except RuntimeError as e:
            logger.error(f"Error resetting miniscreen: {e}")

        if self.root.is_screensaver_running:
            self.root.stop_screensaver()

        self.brighten()
        self.restart_dimming_timer()
        self.display()

    def display(self):
        if self.user_has_control:
            return

        try:
            super().display()

        # When performing actions sometimes the spi addresses can change; this
        # causes a BrokenPipeError because the miniscreen instance tries to send
        # commands to an old SPI address.
        except BrokenPipeError as e:
            logger.error(e)

            # stop the app so that systemd can restart the service
            self.stop(e)

    def stop(self, error=None):
        super().stop(error)
        self.stop_timers()

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
        if isinstance(self.dimming_timer, Timer):
            self.dimming_timer.cancel()
            self.dimming_timer = None

        if isinstance(self.screensaver_timer, Timer):
            self.screensaver_timer.cancel()
            self.screensaver_timer = None
