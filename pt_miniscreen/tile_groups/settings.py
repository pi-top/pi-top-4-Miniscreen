import logging

from ..event import AppEvents, subscribe
from ..tiles import MenuTile, SettingsMenuTile, SettingsTitleBarTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class SettingsTileGroup(TileGroup):
    def __init__(
        self,
        size,
    ):

        self.menu_tile_stack = list()

        self.title_bar_height = 19
        root_menu_tile = SettingsMenuTile(
            size=(size[0], size[1] - self.title_bar_height),
            pos=(0, self.title_bar_height),
        )

        self.menu_tile_stack.append(root_menu_tile)

        title_bar_tile = SettingsTitleBarTile(
            size=(size[0], self.title_bar_height),
            pos=(0, 0),
        )

        def update_title_bar_text():
            title_bar_tile.text = title_bar_tile.delimiter.join(
                [tile.menu.name.capitalize() for tile in self.menu_tile_stack]
            )

        def handle_go_to_child(menu_cls):
            self.menu_tile_stack.append(
                MenuTile(
                    menu_cls=menu_cls,
                    size=(
                        self.current_menu_tile.size[0],
                        self.current_menu_tile.size[1] - self.title_bar_height,
                    ),
                    pos=(0, self.title_bar_height),
                )
            )

            if title_bar_tile.append_title:
                update_title_bar_text()

        def handle_go_to_parent(_):
            self.menu_tile_stack.pop()
            if title_bar_tile.append_title:
                update_title_bar_text()

        subscribe(AppEvents.GO_TO_CHILD_MENU, handle_go_to_child)
        subscribe(AppEvents.GO_TO_PARENT_MENU, handle_go_to_parent)

        super().__init__(
            size=size, menu_tile=root_menu_tile, title_bar_tile=title_bar_tile
        )

    @property
    def current_menu_tile(self):
        return self.menu_tile_stack[-1]
