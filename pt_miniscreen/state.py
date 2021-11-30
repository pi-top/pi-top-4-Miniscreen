import logging
from enum import Enum
from os import path
from pathlib import Path
from time import perf_counter
from typing import Callable

from .event import AppEvent, post_event, subscribe

logger = logging.getLogger(__name__)


class ActivityTimer:
    def __init__(self):
        self.last_active_time = perf_counter()

    def touch(self):
        self.last_active_time = perf_counter()

    @property
    def elapsed_time(self):
        return perf_counter() - self.last_active_time


class State(Enum):
    BOOTSPLASH = 0
    ACTIVE = 1
    DIM = 2
    SCREENSAVER = 3
    WAKING = 4
    RUNNING_ACTION = 5


class Speeds(Enum):
    DYNAMIC_PAGE_REDRAW = 1
    SCROLL = 0.004
    SCREENSAVER = 0.05
    ACTION_STATE_UPDATE = 0.5
    MARQUEE = 0.1


class StateManager:
    def __init__(self, contrast_change_func):
        self.contrast_change_func = contrast_change_func

        self.user_activity_timer = ActivityTimer()
        self.action_timer = ActivityTimer()
        self._state = State.ACTIVE

        self.bootsplash_breadcrumb = "/tmp/.com.pi-top.pt_miniscreen.boot-played"

        if not path.exists(self.bootsplash_breadcrumb):
            self.state = State.BOOTSPLASH

        self.setup_events()

    def setup_events(self):
        def start_current_menu_action(_) -> None:
            logger.debug("Setting state to RUNNING_ACTION")
            self.state = State.RUNNING_ACTION
            self.action_timer.touch()

        def handle_stop_bootsplash(_):
            Path(self.bootsplash_breadcrumb).touch()
            self.state = State.ACTIVE

        subscribe(AppEvent.BUTTON_ACTION_START, start_current_menu_action)
        subscribe(AppEvent.STOP_BOOTSPLASH, handle_stop_bootsplash)

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        if self._state == new_state:
            return

        logger.debug(f"New display state: {new_state}")
        self.user_activity_timer.touch()

        if new_state == State.BOOTSPLASH:
            post_event(AppEvent.START_BOOTSPLASH)

        if new_state == State.SCREENSAVER:
            post_event(AppEvent.START_SCREENSAVER)

        elif self._state == State.SCREENSAVER:
            post_event(AppEvent.STOP_SCREENSAVER)

        self._state = new_state

    def handle_button_press(self, event: AppEvent, handle_event: Callable) -> None:
        if self.state != State.WAKING:
            self.user_activity_timer.touch()
        if self.state == State.ACTIVE:
            handle_event(event)
        self.wake()

    @property
    def is_sleeping(self) -> bool:
        return self.state in [
            State.DIM,
            State.SCREENSAVER,
        ]

    def sleep(self) -> None:
        if not self.is_sleeping:
            logger.debug("Going to sleep...")
            self.contrast_change_func(0)
            self.state = State.DIM

    def wake(self) -> None:
        if self.is_sleeping:
            logger.debug("Waking up...")
            self.contrast_change_func(255)
            self.state = State.WAKING
