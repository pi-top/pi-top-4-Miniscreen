from enum import Enum, auto
from typing import Dict, List


class AppEvents(Enum):
    SELECT_BUTTON_PRESS = auto()  # callable
    CANCEL_BUTTON_PRESS = auto()  # callable
    UP_BUTTON_PRESS = auto()  # callable
    DOWN_BUTTON_PRESS = auto()  # callable
    BUTTON_ACTION_START = auto()  # None
    UPDATE_DISPLAYED_IMAGE = auto()  # None
    GO_TO_CHILD_MENU = auto()  # str
    GO_TO_PARENT_MENU = auto()  # None


subscribers: Dict[AppEvents, List] = dict()


def subscribe(event_type: AppEvents, fn):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)


def post_event(event_type: AppEvents, data=None):
    if event_type not in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(data)
