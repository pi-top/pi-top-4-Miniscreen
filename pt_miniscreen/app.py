import logging
import time
from os import environ
from signal import SIGINT, SIGTERM, signal
from threading import Event, Thread

from imgcat import imgcat
from pitop import Pitop

from .event import AppEvent, post_event, subscribe
from .state import State, StateManager
from .tile_groups import (
    HUDTileGroup,
    PitopBootsplashTileGroup,
    SettingsTileGroup,
    StarfieldScreensaverTileGroup,
)

logger = logging.getLogger(__name__)


class App:
    TIMEOUTS = {
        State.DIM: 20,
        State.SCREENSAVER: 60,
        State.WAKING: 0.6,
        State.RUNNING_ACTION: 30,
    }

    def __init__(self):
        logger.debug("Initializing app...")

        logger.debug("Setting ENV VAR to use miniscreen as system...")
        environ["PT_MINISCREEN_SYSTEM"] = "1"

        self.__stop = False
        self.last_shown_image = None
        self.user_gave_back_control_event = Event()
        self.tile_group_stack = list()

        logger.debug("Initializing miniscreen...")
        self.miniscreen = Pitop().miniscreen

        logger.debug("Initializing rest of app...")
        self.__thread = Thread(target=self._main, args=())

        self._add_tile_group_to_stack_from_cls(HUDTileGroup)

        self.setup_events()

        self.state_manager = StateManager(self.miniscreen.contrast)

        logger.debug("Done initializing app")

    def add_tile_group(self, tile_group):
        if len(self.tile_group_stack) > 0:
            self.current_tile_group.active = False
        self.tile_group_stack.append(tile_group)

        self.current_tile_group.active = True
        post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    def pop_tile_group(self):
        self.current_tile_group.active = False

        if len(self.tile_group_stack) > 1:
            self.tile_group_stack.pop()
        else:
            self._add_tile_group_to_stack_from_cls(SettingsTileGroup)

        self.current_tile_group.active = True
        post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    def _add_tile_group_to_stack_from_cls(self, tile_group_class):
        self.add_tile_group(tile_group_class(size=self.miniscreen.size))

    def setup_events(self) -> None:
        subscribe(
            AppEvent.START_BOOTSPLASH,
            lambda _: self._add_tile_group_to_stack_from_cls(PitopBootsplashTileGroup),
        )
        subscribe(AppEvent.STOP_BOOTSPLASH, lambda _: self.pop_tile_group())

        subscribe(
            AppEvent.START_SCREENSAVER,
            lambda: self._add_tile_group_to_stack_from_cls(
                StarfieldScreensaverTileGroup
            ),
        )
        subscribe(AppEvent.STOP_SCREENSAVER, lambda _: self.pop_tile_group())

        def set_is_user_controlled(user_has_control) -> None:
            if self.user_has_control and not user_has_control:
                self.user_gave_back_control_event.set()

            logger.info(
                f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
            )

        self.miniscreen.when_user_controlled = lambda: set_is_user_controlled(True)
        self.miniscreen.when_system_controlled = lambda: set_is_user_controlled(False)

        def handle_event(event: AppEvent):
            logger.debug(
                f"Handling event {event.name} for tile group {self.current_tile_group}"
            )

            handler = {
                AppEvent.CANCEL_BUTTON_PRESS: self.current_tile_group.handle_cancel_btn,
                AppEvent.SELECT_BUTTON_PRESS: self.current_tile_group.handle_select_btn,
                AppEvent.UP_BUTTON_PRESS: self.current_tile_group.handle_up_btn,
                AppEvent.DOWN_BUTTON_PRESS: self.current_tile_group.handle_down_btn,
            }[event]

            if not handler() and event == AppEvent.CANCEL_BUTTON_PRESS:
                logger.debug(
                    "Button press not handled by current tile group - going to next tile group"
                )
                self.pop_tile_group()
            post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)
            post_event(event)

        self.miniscreen.cancel_button.when_released = (
            lambda: self.state_manager.handle_button_press(
                AppEvent.CANCEL_BUTTON_PRESS, handle_event
            )
        )
        self.miniscreen.select_button.when_released = (
            lambda: self.state_manager.handle_button_press(
                AppEvent.SELECT_BUTTON_PRESS, handle_event
            )
        )
        self.miniscreen.up_button.when_released = (
            lambda: self.state_manager.handle_button_press(
                AppEvent.UP_BUTTON_PRESS, handle_event
            )
        )
        self.miniscreen.down_button.when_released = (
            lambda: self.state_manager.handle_button_press(
                AppEvent.DOWN_BUTTON_PRESS, handle_event
            )
        )

    @property
    def current_tile_group(self):
        return self.tile_group_stack[-1]

    def start(self) -> None:
        if self.__stop:
            return

        logger.debug("Configuring interrupt signals...")
        signal(SIGINT, lambda signal, frame: self.stop())
        signal(SIGTERM, lambda signal, frame: self.stop())

        logger.debug("Starting main app thread...")
        self.__thread = Thread(target=self._main, args=())
        self.__thread.daemon = True
        self.__thread.start()

    def stop(self) -> None:
        if self.__stop:
            return

        logger.info("Stopping app...")
        self.__stop = True

    @property
    def user_has_control(self) -> bool:
        return self.miniscreen.is_active

    def _main(self) -> None:
        logger.info("Starting main loop...")
        while not self.__stop:

            if self.user_has_control:
                logger.info(
                    "User has control. Waiting for user to give control back..."
                )
                self.user_gave_back_control_event.wait()
                self.reset()

            logger.debug(f"Current state: {self.state_manager.state}")

            self.display(self.current_tile_group.image)
            if environ.get("IMGCAT", "0") == "1":
                print("\033c")
                imgcat(self.current_tile_group.image)

            logger.debug("Waiting until image to display has changed...")
            start = time.time()
            self.current_tile_group.wait_until_should_redraw()
            end = time.time()
            logger.debug(f"Image to display has changed! Wait time: {end - start}")

    def display(self, image, wake=False) -> None:
        if wake:
            self.state_manager.wake()

        try:
            self.miniscreen.device.display(image)
        except RuntimeError:
            if not self.__stop:
                raise

        self.last_shown_image = image

    def reset(self) -> None:
        logger.info("Forcing full state refresh...")
        self.state_manager.wake()
        self.miniscreen.reset()
        if self.last_shown_image is not None:
            self.display(self.last_shown_image)
        logger.info("OLED control restored")
