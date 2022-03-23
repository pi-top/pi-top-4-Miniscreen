import logging
from enum import Enum, auto
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class AppEvent(Enum):
    # Action page -> app (for state change)
    ACTION_START = auto()  # callable
    # App -> action page (for UI change)
    ACTION_FINISH = auto()  # callable
    ACTION_TIMEOUT = auto()  # callable
    # Hotspots -> app (for redraw)
    UPDATE_DISPLAYED_IMAGE = auto()  # None
    # Menu page -> menu tile group (for pushing to menu tile stack)
    GO_TO_CHILD_MENU = auto()  # str
    GO_TO_PARENT_MENU = auto()  # None
    # Scrolling
    SCROLL_START = auto()
    SCROLL_END = auto()
    # State manager -> app (for pushing to tile group stack)
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


def unsubscribe_all():
    global subscribers
    subscribers = dict()
