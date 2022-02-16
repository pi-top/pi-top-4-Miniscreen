import datetime
import logging
import time
from enum import Enum, auto
from os import environ
from pathlib import Path
from signal import SIGINT, SIGTERM, signal
from threading import Event, Thread
from typing import Optional

from pitop import Pitop

from .event import AppEvent, post_event, subscribe
from .state import StateManager
from .tile_groups import (
    HUDTileGroup,
    PitopBootsplashTileGroup,
    StarfieldScreensaverTileGroup,
)

logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        logger.debug("Initializing app...")

        logger.debug("Setting ENV VAR to use miniscreen as system...")
        environ["PT_MINISCREEN_SYSTEM"] = "1"

        self.timestamp = (
            str(datetime.datetime.now())
            .split(".")[0]
            .replace(" ", "_")
            .replace(":", "-")
        )
        self.saved_cache_frame_no = 1
        self.last_shown_image = None
        self.user_gave_back_control_event = Event()
        self.tile_group_stack = list()

        logger.debug("Initializing miniscreen...")
        self.miniscreen = Pitop().miniscreen

        logger.debug("Initializing rest of app...")
        self._add_tile_group_to_stack_from_cls(HUDTileGroup)

        self.setup_events()

        self.state_manager = StateManager(self.miniscreen.contrast)

        logger.debug("Done initializing app")

    def add_tile_group(self, tile_group) -> None:
        if len(self.tile_group_stack) > 0:
            self.current_tile_group.active = False
        self.tile_group_stack.append(tile_group)

        self.current_tile_group.active = True
        post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    def pop_tile_group(self) -> None:
        self.current_tile_group.active = False

        if len(self.tile_group_stack) > 1:
            self.tile_group_stack.pop()

        self.current_tile_group.active = True
        post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)

    def _add_tile_group_to_stack_from_cls(self, tile_group_class) -> None:
        self.add_tile_group(tile_group_class(size=self.miniscreen.size))

    def setup_events(self) -> None:
        subscribe(
            AppEvent.START_BOOTSPLASH,
            lambda: self._add_tile_group_to_stack_from_cls(PitopBootsplashTileGroup),
        )
        subscribe(AppEvent.STOP_BOOTSPLASH, lambda: self.pop_tile_group())

        subscribe(
            AppEvent.START_SCREENSAVER,
            lambda: self._add_tile_group_to_stack_from_cls(
                StarfieldScreensaverTileGroup
            ),
        )
        subscribe(AppEvent.STOP_SCREENSAVER, lambda: self.pop_tile_group())

        def set_is_user_controlled(user_has_control) -> None:
            if not user_has_control:
                self.user_gave_back_control_event.set()

            logger.info(
                f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
            )

        self.miniscreen.when_user_controlled = lambda: set_is_user_controlled(True)
        self.miniscreen.when_system_controlled = lambda: set_is_user_controlled(False)

        class MiniscreenButton(Enum):
            UP = auto()
            DOWN = auto()
            SELECT = auto()
            CANCEL = auto()

        def handle_button_press(button: MiniscreenButton):
            logger.debug(
                f"Handling button {button} for tile group {self.current_tile_group}"
            )

            if not getattr(self, "state_manager", None):
                logger.info("Button press before State manager initialised")
                return

            if not self.state_manager.buttons_should_be_handled():
                logger.info("State manager says that buttons should not be handled")
                return

            self.state_manager.wake()

            handler = {
                MiniscreenButton.CANCEL: self.current_tile_group.handle_cancel_btn,
                MiniscreenButton.SELECT: self.current_tile_group.handle_select_btn,
                MiniscreenButton.UP: self.current_tile_group.handle_up_btn,
                MiniscreenButton.DOWN: self.current_tile_group.handle_down_btn,
            }[button]

            if not handler() and button == MiniscreenButton.CANCEL:
                logger.debug(
                    "Button press not handled by current tile group - going to next tile group"
                )
                self.pop_tile_group()

        self.miniscreen.cancel_button.when_released = lambda: handle_button_press(
            MiniscreenButton.CANCEL
        )
        self.miniscreen.select_button.when_released = lambda: handle_button_press(
            MiniscreenButton.SELECT
        )
        self.miniscreen.up_button.when_released = lambda: handle_button_press(
            MiniscreenButton.UP
        )
        self.miniscreen.down_button.when_released = lambda: handle_button_press(
            MiniscreenButton.DOWN
        )

    @property
    def current_tile_group(self):
        return self.tile_group_stack[-1]

    def start(self) -> None:
        self.__stop_event = Event()

        logger.debug("Configuring interrupt signals...")
        signal(SIGINT, lambda signal, frame: self.stop())
        signal(SIGTERM, lambda signal, frame: self.stop())

        logger.debug("Starting main app thread...")
        self.__thread = Thread(target=self._main, args=(), daemon=True)
        self.__thread.start()

    def wait_for_stop(self) -> None:
        self.__stop_event.wait()
        error = getattr(self, "_stop_error", None)
        if isinstance(error, Exception):
            raise error

    def stop(self, error: Optional[Exception] = None) -> None:
        logger.info("Stopping app...")
        self._stop_error = error
        self.__stop_event.set()

    @property
    def user_has_control(self) -> bool:
        return self.miniscreen.is_active

    def _main(self) -> None:
        logger.info("Starting main loop...")
        while not self.__stop_event.is_set():
            if self.user_has_control:
                logger.info(
                    "User has control. Waiting for user to give control back..."
                )
                self.user_gave_back_control_event.wait()
                self.user_gave_back_control_event.clear()
                self.reset()

            logger.debug(f"Current state: {self.state_manager.state}")

            self.display(self.current_tile_group.image)
            if environ.get("IMGCAT", "0") == "1":
                print("")
                from imgcat import imgcat

                imgcat(self.current_tile_group.image)

            if environ.get("SAVE_CACHE", "0") == "1":
                p = Path(f"/tmp/pt-miniscreen/{self.timestamp}")
                p.mkdir(parents=True, exist_ok=True)

                self.current_tile_group.image.save(
                    p / f"{str(self.saved_cache_frame_no).zfill(4)}.png"
                )
                self.saved_cache_frame_no += 1

            logger.debug("Waiting until image to display has changed...")
            start = time.time()
            self.current_tile_group.wait_until_should_redraw(timeout=1)
            end = time.time()
            logger.debug(f"Image to display has changed! Wait time: {end - start}")

    def display(self, image, wake=False) -> None:
        if wake:
            self.state_manager.wake()

        self.last_shown_image = image

        try:
            self.miniscreen.device.display(image)
        except (RuntimeError, BrokenPipeError) as e:
            # can't draw to miniscreen, reset won't help, just die
            logger.error(f"app.display: {e}")
            self.stop(e)

    def reset(self) -> None:
        logger.info("Forcing full state refresh...")
        self.state_manager.wake()
        try:
            self.miniscreen.reset()
        except RuntimeError as e:
            logger.error(f"Error resetting miniscreen: {e}")

        if self.last_shown_image is not None:
            self.display(self.last_shown_image)
        logger.info("OLED control restored")
