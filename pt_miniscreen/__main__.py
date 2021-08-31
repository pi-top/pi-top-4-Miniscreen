from logging import ERROR, getLogger
from os import path
from pathlib import Path
from signal import SIGINT, SIGTERM, signal

import click
from ConfigParser import ConfigParser
from pitop import Pitop
from pitop.common.logger import PTLogger

# TODO: drop/override 'DeviceNotFoundError' to avoid awkward luma.core import
from pitop.miniscreen.oled.core.contrib.luma.core.error import DeviceNotFoundError

from . import MiniscreenApp
from .widgets.common.functions import get_image_file_path

config_file = "/etc/pt-miniscreen/settings.ini"


def configure_interrupt_signals(app):
    def signal_handler(signal, frame):
        PTLogger.debug("Stopping...")
        app.stop()
        PTLogger.debug("Stopped!")

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)


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
            pass

        Path(self.has_played_breadcrumb).touch()


@click.command()
@click.option(
    "--log-level",
    type=int,
    help="set logging level from 10 (more verbose) to 50 (less verbose)",
    default=20,
    show_default=True,
)
@click.version_option()
def main(log_level) -> None:
    # Ignore PIL debug messages
    getLogger("PIL").setLevel(ERROR)
    PTLogger.setup_logging(
        logger_name="pt-miniscreen", logging_level=log_level, log_to_journal=False
    )

    try:
        miniscreen = Pitop().miniscreen
    except DeviceNotFoundError as e:
        PTLogger.error(f"Error getting device: {str(e)}")
        return

    bootsplash_path = get_image_file_path("startup/pi-top_startup.gif")
    if path.exists(config_file):
        config = ConfigParser().read(config_file)
        try:
            bootsplash_path = config.get("Bootsplash", "Path")
        except Exception:
            pass

    splash = Bootsplash(bootsplash_path, miniscreen)

    if not splash.has_played():
        PTLogger.info("Not played boot animation this session - starting...")
        splash.play()
        PTLogger.info("Finished startup animation")

    app = MiniscreenApp(miniscreen)
    configure_interrupt_signals(app)

    app.main_loop()
    app.stop()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
