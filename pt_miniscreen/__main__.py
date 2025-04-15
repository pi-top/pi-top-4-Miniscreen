import logging
from os import environ
from typing import Union
import click
import click_logging
from pitop.system.pitop import Pitop
from pitop.common.pt_os import is_pi_top_os


from .app import App
from .welcome.app import WelcomeApp
from .state import StateManager

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
logging.getLogger("pitop.common").setLevel(logging.INFO)


def run(cls: Union[type[App], type[WelcomeApp]], miniscreen: Pitop.miniscreen) -> None:
    app = cls(miniscreen)
    app.start()
    app.wait_for_stop()


def should_run_welcome_app():
    return (
        # don't run on Raspberry Pi OS or other OSes
        is_pi_top_os()
        # read the first_boot value in the state file
        and (
            StateManager(package_name="pt-miniscreen").get("app", "first_boot", "true")
            == "true"
        )
    )


def set_first_boot_done():
    StateManager(package_name="pt-miniscreen").set("app", "first_boot", "false")


@click.command()
@click_logging.simple_verbosity_option(logger)
@click.version_option()
def main() -> None:
    logger.debug("Setting ENV VAR to use miniscreen as system...")
    environ["PT_MINISCREEN_SYSTEM"] = "1"
    miniscreen = Pitop().miniscreen

    if should_run_welcome_app():
        run(WelcomeApp, miniscreen)
        set_first_boot_done()
    run(App, miniscreen)


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
