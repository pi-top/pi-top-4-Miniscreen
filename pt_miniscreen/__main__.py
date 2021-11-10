import logging
from configparser import ConfigParser
from logging import ERROR, getLogger
from os import path
from signal import SIGINT, SIGTERM, signal

import click
from pitop import Pitop

# TODO: drop/override 'DeviceNotFoundError' to avoid awkward luma.core import
from pitop.miniscreen.oled.core.contrib.luma.core.error import DeviceNotFoundError

from . import MiniscreenApp
from .bootsplash import Bootsplash
from .widgets.common.functions import get_image_file_path

logger = logging.getLogger()
config_file = "/etc/pt-miniscreen/settings.ini"


def configure_interrupt_signals(app):
    def signal_handler(signal, frame):
        logger.debug("Stopping...")
        app.stop()
        logger.debug("Stopped!")

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)


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

    try:
        miniscreen = Pitop().miniscreen
    except DeviceNotFoundError as e:
        logger.error(f"Error getting device: {str(e)}")
        return

    bootsplash_path = get_image_file_path("startup/pi-top_startup.gif")
    if path.exists(config_file):
        config = ConfigParser()
        config.read(config_file)
        try:
            bootsplash_path = config.get("Bootsplash", "Path")
        except Exception:
            pass

    splash = Bootsplash(bootsplash_path, miniscreen)

    if not splash.has_played():
        logger.info("Not played boot animation this session - starting...")
        splash.play()
        logger.info("Finished startup animation")

    app = MiniscreenApp(miniscreen)
    configure_interrupt_signals(app)

    app.main_loop()
    app.stop()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
