import logging
from enum import Enum
from time import perf_counter

logger = logging.getLogger(__name__)


class ActivityTimer:
    def __init__(self):
        self.last_active_time = perf_counter()

    def reset(self):
        self.last_active_time = perf_counter()

    @property
    def elapsed_time(self):
        return perf_counter() - self.last_active_time


class DisplayState(Enum):
    ACTIVE = 1
    DIM = 2
    SCREENSAVER = 3
    WAKING = 4
    RUNNING_ACTION = 5


class Speeds(Enum):
    DYNAMIC_PAGE_REDRAW = 1
    SCROLL = 0.004
    SKIP = 0.001
    SCREENSAVER = 0.05
    MARQUEE = 0.1


class DisplayStateManager:
    def __init__(self):
        self.user_activity_timer = ActivityTimer()
        self.action_timer = ActivityTimer()
        self._state = DisplayState.ACTIVE

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if self._state != new_state:
            logger.debug(f"New display state: {new_state}")
            self.user_activity_timer.reset()

        self._state = new_state
