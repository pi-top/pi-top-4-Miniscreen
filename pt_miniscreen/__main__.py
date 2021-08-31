from logging import ERROR, getLogger
from signal import SIGINT, SIGTERM, signal

import click
from pitop import Pitop
from pitop.common.logger import PTLogger

# TODO: drop/override 'DeviceNotFoundError' to avoid awkward luma.core import
from pitop.miniscreen.oled.core.contrib.luma.core.error import DeviceNotFoundError

from . import MiniscreenApp


def configure_interrupt_signals(app):
    def signal_handler(signal, frame):
        PTLogger.debug("Stopping...")
        app.stop()
        PTLogger.debug("Stopped!")

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
    PTLogger.setup_logging(
        logger_name="pt-miniscreen", logging_level=log_level, log_to_journal=False
    )

    try:
        miniscreen = Pitop().miniscreen
    except DeviceNotFoundError as e:
        PTLogger.error(f"Error getting device: {str(e)}")
        return

    app = MiniscreenApp(miniscreen)
    configure_interrupt_signals(app)

    app.main_loop()
    app.stop()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
