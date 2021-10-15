import logging
from signal import SIGINT, SIGTERM, pause, signal

import click
import click_logging

from . import App

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)


def configure_interrupt_signals(app):
    logger.info("Configuring interrupt signals...")

    def signal_handler(signal, frame):
        logger.debug("Stopping...")
        app.stop()
        logger.debug("Stopped!")

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)


@click.command()
@click_logging.simple_verbosity_option(logger)
@click.version_option()
def main() -> None:
    # Ignore PIL debug messages
    logging.getLogger("PIL").setLevel(logging.ERROR)

    logger.debug("Creating app...")
    app = App()
    configure_interrupt_signals(app)
    logger.info("Starting app...")
    app.start()
    logger.info("App is now running...")
    pause()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
