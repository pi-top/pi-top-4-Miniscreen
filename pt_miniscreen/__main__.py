from argparse import ArgumentParser
from logging import ERROR, getLogger
from signal import SIGINT, SIGTERM, signal

import click

# TODO: drop/override 'DeviceNotFoundError' to avoid awkward luma.core import
from pitop.miniscreen.oled.core.contrib.luma.core.error import DeviceNotFoundError
from pitop import Miniscreen

from pitop.common.logger import PTLogger

from . import MiniscreenApp


def configure_interrupt_signals(app):
    def signal_handler(signal, frame):
        PTLogger.debug("Stopping...")
        app.stop()
        PTLogger.debug("Stopped!")

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)


def get_parser():
    parser = ArgumentParser(description="pi-top [4] Miniscreen App")
    parser.add_argument(
        "--log-level",
        type=int,
        help="set logging level from 10 (more verbose) to 50 (less verbose)",
        default=20,
    )
    return parser


@click.command()
@click.version_option()
def main(prog_name) -> None:
    args = get_parser().parse_args()

    # Ignore PIL debug messages
    getLogger("PIL").setLevel(ERROR)
    PTLogger.setup_logging(
        logger_name=prog_name, logging_level=args.log_level, log_to_journal=False
    )

    try:
        miniscreen = Miniscreen()
    except DeviceNotFoundError as e:
        PTLogger.error(f"Error getting device: {str(e)}")
        return

    app = MiniscreenApp(miniscreen)
    configure_interrupt_signals(app)

    app.main_loop()
    app.stop()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
