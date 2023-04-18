from enum import auto, Enum


class ProjectState(Enum):
    IDLE = auto()
    STARTING = auto()
    RUNNING_WITH_INSTRUCTIONS_IN_SCREEN = auto()
    RUNNING_WITH_CLEAR_SCREEN = auto()
    STOPPING = auto()
    ERROR = auto()


class ProjectExitCondition(Enum):
    FLICK_POWER = auto()
    HOLD_CANCEL = auto()
    NONE = auto()
