import logging
from signal import pause

import click
import click_logging

from .app import App

logger = logging.getLogger()
click_logging.basic_config(logger)

# Ignore PIL debug messages -
# STREAM b'IHDR' 16 13
# STREAM b'IDAT' 41 107
# STREAM b'IHDR' 16 13
# STREAM b'IDAT' 41 114
# STREAM b'IHDR' 16 13
# STREAM b'IDAT' 41 121
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("pitop").setLevel(logging.INFO)

@click.command()
@click_logging.simple_verbosity_option(logger)
@click.version_option()
def main() -> None:
    app = App()
    app.start()
    pause()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
