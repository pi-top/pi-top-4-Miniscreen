from enum import Enum, auto
from os import path
from pathlib import Path
from functools import partial
from typing import Any


def get_project_root() -> Path:
    return Path(__file__).parent


def get_image_file_path(relative_file_name: str) -> str:
    return path.abspath(path.join(get_project_root(), "images", relative_file_name))


def isclass(obj: Any, cls: Any) -> bool:
    return (
        isinstance(obj, partial) and issubclass(obj.func, cls) or isinstance(obj, cls)
    )


class ButtonEvents(Enum):
    UP_PRESS = auto()
    UP_RELEASE = auto()
    DOWN_PRESS = auto()
    DOWN_RELEASE = auto()
    CANCEL_PRESS = auto()
    CANCEL_RELEASE = auto()
    SELECT_PRESS = auto()
    SELECT_RELEASE = auto()
