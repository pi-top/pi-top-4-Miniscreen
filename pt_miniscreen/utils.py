from os import path
from pathlib import Path
from time import time


def get_project_root() -> Path:
    return Path(__file__).parent


def get_image_file_path(relative_file_name: str) -> str:
    return path.abspath(path.join(get_project_root(), "images", relative_file_name))


class Stopwatch:
    def __init__(self) -> None:
        self.time_start = 0.0

    def start(self) -> None:
        self.time_start = time()

    def elapsed(self) -> float:
        if self.time_start > 0:
            return time() - self.time_start
        return 0.0
