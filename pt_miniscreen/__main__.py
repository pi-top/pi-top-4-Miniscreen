import logging
from signal import pause

import click
import click_logging

from .app import App

logger = logging.getLogger()
click_logging.basic_config(logger)


@click.command()
@click_logging.simple_verbosity_option(logger)
@click.version_option()
def main() -> None:
    app = App()
    app.start()
    pause()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
