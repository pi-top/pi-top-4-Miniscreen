from enum import Enum, auto


class ActionState(Enum):
    UNKNOWN = auto()
    PROCESSING = auto()
    ENABLED = auto()
    DISABLED = auto()
    SUBMIT = auto()
