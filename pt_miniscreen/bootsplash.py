from os import path
from pathlib import Path

from pitop.common.logger import PTLogger


class Bootsplash:
    has_played_breadcrumb = "/tmp/.com.pi-top.pt_miniscreen.boot-played"

    def __init__(self, path, miniscreen):
        self.path = path
        self.miniscreen = miniscreen

    def has_played(self):
        return path.exists(self.has_played_breadcrumb)

    def play(self):
        try:
            self.miniscreen.play_animated_image_file(
                self.path, background=False, loop=False
            )
        except Exception as e:
            PTLogger.warning(f"Unable to play miniscreen startup animation: {e}")

        Path(self.has_played_breadcrumb).touch()
