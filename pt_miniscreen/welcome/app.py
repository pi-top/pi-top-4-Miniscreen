import logging
import traceback
from os import environ

from pitop.system.pitop import Pitop
from pt_miniscreen.utils import ButtonEvents

from ..core import App as BaseApp
from .root import WelcomeRootComponent

logger = logging.getLogger(__name__)


class WelcomeApp(BaseApp):
    DIMMING_TIMEOUT = 20

    def __init__(self, miniscreen=None):
        self.miniscreen = miniscreen
        if miniscreen is None:
            logger.debug("Setting ENV VAR to use miniscreen as system...")
            environ["PT_MINISCREEN_SYSTEM"] = "1"
            logger.debug("Initializing miniscreen...")
            self.miniscreen = Pitop().miniscreen
        assert self.miniscreen is not None

        self.user_has_control = False

        def set_is_user_controlled(user_has_control) -> None:
            self.user_has_control = user_has_control
            if not user_has_control:
                self._restore_miniscreen()

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

        logger.debug("Initialising app...")
        super().__init__(
            display=self.miniscreen.device.display,
            Root=WelcomeRootComponent,
            size=self.miniscreen.size,
        )

    def _restore_miniscreen(self):
        try:
            self.miniscreen.reset()
        except RuntimeError as e:
            logger.error(f"Error resetting miniscreen: {e}")

        self.display()

    def create_button_handler(self, func):
        def handler():
            if self.user_has_control:
                logger.debug("User has control of miniscreen, omitting button press...")
                return

            try:
                if callable(func):
                    func()

                if self.root.should_exit:
                    logger.debug("Stopping 'welcome' app...")
                    self.stop()

            except Exception as e:
                logger.error(f"Error in button handler: {e}")
                traceback.print_exc()
                self.stop(e)

        return handler
