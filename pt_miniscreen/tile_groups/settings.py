import logging

from ..event import AppEvent, subscribe
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

        self.title_bar_tile = SettingsTitleBarTile(
            size=(size[0], self.title_bar_height),
            pos=(0, 0),
        )

        def handle_go_to_child(menu_cls):
            self.current_menu_tile.active = False
            self.menu_tile_stack.append(
                MenuTile(
                    menu_cls=menu_cls,
                    size=(
                        size[0],
                        size[1] - self.title_bar_height,
                    ),
                    pos=(0, self.title_bar_height),
                )
            )
            self.current_menu_tile.active = True
            if self.title_bar_tile.append_title:
                self.update_title_bar_text()

        subscribe(AppEvent.GO_TO_CHILD_MENU, handle_go_to_child)

        super().__init__(
            size=size, menu_tile=root_menu_tile, title_bar_tile=self.title_bar_tile
        )

    def update_title_bar_text(self):
        self.title_bar_tile.text = self.title_bar_tile.delimiter.join(
            [tile.menu.name.capitalize() for tile in self.menu_tile_stack]
        )

    @property
    def current_menu_tile(self):
        return self.menu_tile_stack[-1]

    def handle_cancel_btn(self):
        if len(self.menu_tile_stack) == 1:
            return False

        self.menu_tile_stack.pop()
        self.current_menu_tile.active = True

        if self.title_bar_tile.append_title:
            self.update_title_bar_text()

        return True
