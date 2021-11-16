from enum import Enum


class ActionState(Enum):
    UNKNOWN = 0
    PROCESSING = 1
    ENABLED = 2
    DISABLED = 3
    FINISHED_PROCESSING = 4
