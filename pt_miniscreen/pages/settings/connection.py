from ...tile_group import TileGroup
from ...tiles.settings_connection import SettingsConnectionMenuTile
from ...tiles.settings_title_bar import SettingsTitleBarTile
from ...utils import get_image_file_path
from ..templates.menu.page import Page as PageBase


class Page(PageBase):
    def __init__(self, size):
        super().__init__(
            size=size,
            image_path=get_image_file_path("menu/settings.gif"),
            text="Connection",
            child_tile_group=TileGroup(
                size=(128, 64),
                menu_tile=SettingsConnectionMenuTile((128, 64)),
                title_bar_tile=SettingsTitleBarTile(
                    size=(128, 19),
                    pos=(0, 0),
                    text="Settings / Connection",
                ),
            ),
        )
