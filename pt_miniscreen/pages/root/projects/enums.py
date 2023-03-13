from enum import auto, Enum


class ProjectState(Enum):
    IDLE = auto()
    STARTING = auto()
    RUNNING = auto()
    PROJECT_USES_MINISCREEN = auto()
    STOPPING = auto()
    ERROR = auto()


class ProjectExitCondition(Enum):
    FLICK_POWER = auto()
    HOLD_CANCEL = auto()
    NONE = auto()
