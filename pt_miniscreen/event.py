import logging
from enum import Enum, auto
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class AppEvent(Enum):
    SELECT_BUTTON_PRESS = auto()  # callable
    CANCEL_BUTTON_PRESS = auto()  # callable
    UP_BUTTON_PRESS = auto()  # callable
    DOWN_BUTTON_PRESS = auto()  # callable
    ACTION_START = auto()  # callable
    ACTION_FINISH = auto()  # callable
    ACTION_TIMEOUT = auto()  # callable
    UPDATE_DISPLAYED_IMAGE = auto()  # None
    GO_TO_CHILD_MENU = auto()  # str
    GO_TO_PARENT_MENU = auto()  # None
    START_BOOTSPLASH = auto()  # None
    STOP_BOOTSPLASH = auto()  # None
    START_SCREENSAVER = auto()  # None
    STOP_SCREENSAVER = auto()  # None


subscribers: Dict[AppEvent, List[Callable]] = dict()


def subscribe(event_type: AppEvent, fn: Callable) -> None:
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)


def post_event(event_type: AppEvent, data: Any = None) -> None:
    # logger.debug(f"Posting event: {event_type}")
    if event_type not in subscribers:
        return
    for fn in subscribers[event_type]:
        if data is None:
            fn()
        else:
            fn(data)
