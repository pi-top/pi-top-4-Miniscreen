import logging
from enum import Enum
from os import path
from pathlib import Path
from sched import scheduler
from threading import Thread, currentThread
from time import sleep
from typing import Callable, Union

from .event import AppEvent, post_event, subscribe

logger = logging.getLogger(__name__)


class State(Enum):
    BOOTSPLASH = 0
    ACTIVE = 1
    DIM = 2
    SCREENSAVER = 3
    WAKING = 4
    RUNNING_ACTION = 5


class Speeds(Enum):
    DYNAMIC_PAGE_REDRAW = 1
    SCROLL = 0.017
    SCREENSAVER = 0.05
    ACTION_STATE_UPDATE = 0.5
    MARQUEE = 0.1


class ScheduledEventManager:
    def __init__(self):
        self.sched = scheduler()
        self.sched_event_threads = dict()

    def run_scheduled_event_thread(
        self, delay: Union[int, float], action: Callable
    ) -> None:
        # Replace with event wait?
        sleep(delay)

        if getattr(currentThread(), "do_action", True):
            action()

    def set_sched_event(
        self, name: str, delay: Union[int, float], action: Callable
    ) -> None:
        logger.info(f"Setting up scheduled event '{name}' with delay {delay}...")
        t = Thread(
            target=self.run_scheduled_event_thread, args=(delay, action), daemon=True
        )
        t.start()
        self.sched_event_threads.update({name: t})

    def cancel_sched_event(self, name):
        event_thread = self.sched_event_threads.get(name)
        if event_thread and event_thread.is_alive():
            logger.info(f"Cancelling scheduled event '{name}'")
            event_thread.do_action = False
            self.sched_event_threads.pop(name)


class StateManager:
    TIMEOUTS = {
        State.DIM: 20,
        State.SCREENSAVER: 40,
        State.WAKING: 0.6,
        State.RUNNING_ACTION: 30,
    }

    def __init__(self, contrast_change_func: Callable):
        self.contrast_change_func = contrast_change_func

        self.sched_event_manager = ScheduledEventManager()

        self._state = State.ACTIVE

        self.bootsplash_breadcrumb = "/tmp/.com.pi-top.pt_miniscreen.boot-played"

        if not path.exists(self.bootsplash_breadcrumb):
            self.state = State.BOOTSPLASH

        self.setup_event_listeners()

        self.reset_dim_timer()

    def reset_dim_timer(self) -> None:
        event_key = "dim"
        self.sched_event_manager.cancel_sched_event(event_key)

        self.sched_event_manager.set_sched_event(
            name=event_key,
            delay=self.TIMEOUTS[State.DIM],
            action=self.sleep,
        )

    def reset_screensaver_timer(self) -> None:
        event_key = "screensaver"
        self.sched_event_manager.cancel_sched_event(event_key)

        def set_screensaver_state():
            self.state = State.SCREENSAVER

        self.sched_event_manager.set_sched_event(
            name=event_key,
            delay=self.TIMEOUTS[State.SCREENSAVER],
            action=set_screensaver_state,
        )

    def start_waking_timer(self) -> None:
        event_key = "waking"
        self.sched_event_manager.cancel_sched_event(event_key)

        def set_state_active() -> None:
            self.state = State.ACTIVE

        self.sched_event_manager.set_sched_event(
            name=event_key,
            delay=self.TIMEOUTS[State.WAKING],
            action=set_state_active,
        )

    def start_action_timeout_timer(self) -> None:
        event_key = "action"
        self.sched_event_manager.cancel_sched_event(event_key)

        def set_failed_state() -> None:
            # Do something error-y
            logger.error("Action timed out! Could be bad.")
            self.state = State.ACTIVE

        self.sched_event_manager.set_sched_event(
            name=event_key,
            delay=self.TIMEOUTS[State.RUNNING_ACTION],
            action=set_failed_state,
        )

    def setup_event_listeners(self) -> None:
        def do_action(action_func) -> None:
            logger.error("Setting state to RUNNING_ACTION")
            self.state = State.RUNNING_ACTION
            logger.critical("Running button action function")
            action_func()

        def handle_stop_bootsplash(_) -> None:
            Path(self.bootsplash_breadcrumb).touch()
            self.state = State.ACTIVE

        subscribe(AppEvent.BUTTON_ACTION_START, do_action)
        subscribe(AppEvent.STOP_BOOTSPLASH, handle_stop_bootsplash)

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        if self._state == new_state:
            return

        logger.debug(f"New display state: {new_state}")

        if new_state == State.DIM:
            self.reset_screensaver_timer()

        if self._state == State.DIM:
            self.sched_event_manager.cancel_sched_event("screensaver")

        if new_state == State.WAKING:
            logger.debug("Starting waking timer...")
            self.start_waking_timer()

        if new_state == State.BOOTSPLASH:
            post_event(AppEvent.START_BOOTSPLASH)

        elif new_state == State.SCREENSAVER:
            post_event(AppEvent.START_SCREENSAVER)

        elif self._state == State.SCREENSAVER:
            post_event(AppEvent.STOP_SCREENSAVER)

        elif self.state == State.RUNNING_ACTION:
            logger.critical("WE ARE RUNNING AN ACTION!")
            self.start_action_timeout_timer()
            post_event(AppEvent.STOP_SCREENSAVER)

        self._state = new_state

    def handle_button_press(self, event: AppEvent, handle_event: Callable) -> None:
        if self.state != State.WAKING:
            self.reset_dim_timer()

        self.wake()

        if self.state in [State.ACTIVE, State.DIM]:
            handle_event(event)

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
