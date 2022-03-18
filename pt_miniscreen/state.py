import logging
from dataclasses import dataclass
from enum import Enum, auto
from os import path
from pathlib import Path
from sched import scheduler
from threading import Thread, currentThread
from time import sleep
from typing import Callable, Union

from .event import AppEvent, post_event, subscribe

logger = logging.getLogger(__name__)


class State(Enum):
    BOOTSPLASH = auto()
    ACTIVE = auto()
    DIM = auto()
    SCREENSAVER = auto()
    WAKING = auto()
    RUNNING_ACTION = auto()


class Speeds(Enum):
    DYNAMIC_PAGE_REDRAW = 1
    SCROLL = 0.017
    SCREENSAVER = 0.05
    ACTION_STATE_UPDATE = 0.5
    MARQUEE = 0.1


timeouts = {
    State.DIM: 20,
    State.SCREENSAVER: 40,
    State.WAKING: 0.6,
    State.RUNNING_ACTION: 30,
}


@dataclass
class ScheduledEvent:
    delay: Union[int, float]
    action: Callable


class ScheduledAppEvent(Enum):
    ACTIVATE_DIMMING = auto()
    ACTIVATE_SCREENSAVER = auto()
    FINISH_WAKING = auto()
    HANDLE_ACTION_TIMEOUT = auto()


class ScheduledEventManager:
    def __init__(self):
        self.sched = scheduler()
        self.sched_event_threads = dict()

    def run_scheduled_event_thread(self, event: ScheduledEvent) -> None:
        # Replace with event wait?
        sleep(event.delay)

        if getattr(currentThread(), "do_action", True):
            event.action()

    def set_sched_event(
        self, event_type: ScheduledAppEvent, event: ScheduledEvent
    ) -> None:
        self.cancel_sched_event(event_type)
        logger.debug(
            f"Setting up scheduled event '{event_type}' with delay {event.delay}..."
        )
        t = Thread(target=self.run_scheduled_event_thread, args=(event,), daemon=True)
        t.start()
        self.sched_event_threads.update({event_type: t})

    def cancel_sched_event(self, type: ScheduledAppEvent) -> None:
        event_thread = self.sched_event_threads.get(type)
        if event_thread and event_thread.is_alive():
            logger.debug(f"Cancelling scheduled event '{type}'")
            event_thread.do_action = False
            self.sched_event_threads.pop(type)


class StateManager:
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
        self.sched_event_manager.set_sched_event(
            ScheduledAppEvent.ACTIVATE_DIMMING,
            ScheduledEvent(timeouts[State.DIM], self.sleep),
        )

    def reset_screensaver_timer(self) -> None:
        def set_screensaver_state():
            self.state = State.SCREENSAVER

        self.sched_event_manager.set_sched_event(
            ScheduledAppEvent.ACTIVATE_SCREENSAVER,
            ScheduledEvent(timeouts[State.SCREENSAVER], set_screensaver_state),
        )

    def start_waking_timer(self) -> None:
        def set_state_active() -> None:
            self.state = State.ACTIVE

        self.sched_event_manager.set_sched_event(
            ScheduledAppEvent.FINISH_WAKING,
            ScheduledEvent(timeouts[State.WAKING], set_state_active),
        )

    def start_action_timeout_timer(self) -> None:
        def handle_action_timeout() -> None:
            logger.error("Action timed out!")
            post_event(AppEvent.ACTION_TIMEOUT)
            self.state = State.ACTIVE

        self.sched_event_manager.set_sched_event(
            ScheduledAppEvent.HANDLE_ACTION_TIMEOUT,
            ScheduledEvent(timeouts[State.RUNNING_ACTION], handle_action_timeout),
        )

    def cancel_action_timeout_timer(self) -> None:
        self.sched_event_manager.cancel_sched_event(
            ScheduledAppEvent.HANDLE_ACTION_TIMEOUT
        )

    def setup_event_listeners(self) -> None:
        def do_action(current_page_select_press_func) -> None:
            self.state = State.RUNNING_ACTION
            logger.info("Running page action")
            current_page_select_press_func()
            if self.state == State.RUNNING_ACTION:
                logger.info("Finished running page action")
                self.state = State.ACTIVE
                post_event(AppEvent.ACTION_FINISH)

        def handle_stop_bootsplash() -> None:
            Path(self.bootsplash_breadcrumb).touch()
            self.state = State.ACTIVE

        subscribe(AppEvent.ACTION_START, do_action)
        subscribe(AppEvent.STOP_BOOTSPLASH, handle_stop_bootsplash)

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        if self._state == new_state:
            return

        logger.debug(f"New display state: {new_state}")

        # No longer running action? Cancel timer
        if self._state == State.RUNNING_ACTION:
            self.cancel_action_timeout_timer()

        # Is dim? Start screensaver timer
        if new_state == State.DIM:
            self.reset_screensaver_timer()

        # No longer dim? Cancel screensaver timer
        if self._state == State.DIM:
            self.sched_event_manager.cancel_sched_event(
                ScheduledAppEvent.ACTIVATE_SCREENSAVER
            )

        # Now waking? Start timer to become active
        if new_state == State.WAKING:
            logger.debug("Starting waking timer...")
            self.start_waking_timer()

        # Emit events for states that require changing the tile group
        if new_state == State.BOOTSPLASH:
            post_event(AppEvent.START_BOOTSPLASH)

        elif new_state == State.SCREENSAVER:
            post_event(AppEvent.START_SCREENSAVER)

        elif self._state == State.SCREENSAVER:
            post_event(AppEvent.STOP_SCREENSAVER)

        # Start timer for handling action timeout
        # Emit event
        elif new_state == State.RUNNING_ACTION:
            self.start_action_timeout_timer()

        self._state = new_state

    def buttons_should_be_handled(self):
        return self.state in [State.ACTIVE, State.DIM, State.SCREENSAVER]

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
        self.reset_dim_timer()
