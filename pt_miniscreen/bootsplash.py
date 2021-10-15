import logging
from configparser import ConfigParser
from os import path
from pathlib import Path

from .utils import get_image_file_path

logger = logging.getLogger(__name__)


class Bootsplash:
    has_played_breadcrumb = "/tmp/.com.pi-top.pt_miniscreen.boot-played"
    config_file = "/etc/pt-miniscreen/settings.ini"

    def __init__(self, miniscreen):
        bootsplash_path = get_image_file_path("startup/pi-top_startup.gif")

        if path.exists(self.config_file):
            config = ConfigParser()
            config.read(self.config_file)
            try:
                bootsplash_path = config.get("Bootsplash", "Path")
            except Exception:
                pass

        self.path = bootsplash_path
        self.miniscreen = miniscreen

    def has_played(self):
        return path.exists(self.has_played_breadcrumb)

    def play(self):
        logger.info("Playing boot splash...")
        try:
            self.miniscreen.play_animated_image_file(
                self.path, background=False, loop=False
            )
        except Exception as e:
            logger.warning(f"Unable to play miniscreen startup animation: {e}")

        logger.debug("Finished playing boot splash, touching breadcrumb...")
        Path(self.has_played_breadcrumb).touch()
