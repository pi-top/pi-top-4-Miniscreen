import logging
from os import environ
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
    from pitop import Pitop

    from .tile_group import TileGroup
    from .tile_group_context import TileGroupContext, TileGroupContextManager
    from .tiles import HUDMenuTile, SettingsMenuTile, SettingsTitleBarTile
    from .tiles.settings_connection import SettingsConnectionMenuTile

    logger.debug("Setting ENV VAR to use miniscreen as system...")
    environ["PT_MINISCREEN_SYSTEM"] = "1"

    miniscreen = Pitop().miniscreen

    title_bar_height = 19

    main = TileGroupContext(
        tile_groups=[
            TileGroup(
                size=miniscreen.size,
                menu_tile=HUDMenuTile(size=miniscreen.size),
                title_bar_tile=None,
            ),
            TileGroup(
                size=miniscreen.size,
                title_bar_tile=SettingsTitleBarTile(
                    size=(miniscreen.size[0], title_bar_height),
                    pos=(0, 0),
                ),
                menu_tile=SettingsMenuTile(
                    size=(
                        miniscreen.size[0],
                        miniscreen.size[1] - title_bar_height,
                    ),
                    pos=(0, title_bar_height),
                ),
            ),
        ],
    )
    settings_connection = TileGroupContext(
        name="settings_menu",
        tile_groups=[
            TileGroup(
                size=miniscreen.size,
                menu_tile=SettingsConnectionMenuTile(miniscreen.size),
                title_bar_tile=SettingsTitleBarTile(
                    size=(
                        miniscreen.size[0],
                        miniscreen.size[1] - title_bar_height,
                    ),
                    pos=(0, title_bar_height),
                    text="Settings / Connection",
                ),
            ),
        ],
    )
    context_manager = TileGroupContextManager(contexts=[main, settings_connection])
    app = App(miniscreen=miniscreen, context_manager=context_manager)
    app.start()
    pause()


if __name__ == "__main__":
    main(prog_name="pt-miniscreen")  # pragma: no cover
