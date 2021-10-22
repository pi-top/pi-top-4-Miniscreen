from enum import Enum, auto
from typing import Dict, List


class AppEvents(Enum):
    READY_TO_BE_A_MAKER = auto()  # bool
    OS_UPDATE_SOURCES = auto()  # 'started'/'success'/'failed'
    OS_UPDATER_PREPARE = auto()  # 'started'/'success'/'failed'
    OS_UPDATER_UPGRADE = auto()  # 'started'/'success'/'failed'
    OS_HAS_UPDATES = auto()  # bool
    OS_ALREADY_CHECKED_UPDATES = auto()  # bool
    AP_HAS_SSID = auto()  # string
    AP_HAS_PASSPHRASE = auto()  # string
    HAS_CONNECTED_DEVICE = auto()  # bool
    IS_CONNECTED_TO_INTERNET = auto()  # bool
    RESTARTING_WEB_PORTAL = auto()  # bool
    USER_SKIPPED_CONNECTION_GUIDE = auto()  # bool
    SELECT_BUTTON_PRESS = auto()  # callable
    CANCEL_BUTTON_PRESS = auto()  # callable
    UP_BUTTON_PRESS = auto()  # callable
    DOWN_BUTTON_PRESS = auto()  # callable
    BUTTON_ACTION_START = auto()


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
