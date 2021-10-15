from enum import Enum

from .activity_timer import ActivityTimer


class MenuState(Enum):
    ACTIVE = 1
    DIM = 2
    SCREENSAVER = 3
    WAKING = 4
    RUNNING_ACTION = 5


class Speeds(Enum):
    DYNAMIC_PAGE_REDRAW = 1
    SCROLL = 0.004
    SKIP = 0.001


class MenuStateManager:
    def __init__(self):
        self.user_activity_timer = ActivityTimer()
        self.action_timer = ActivityTimer()
        self.state = MenuState.ACTIVE
