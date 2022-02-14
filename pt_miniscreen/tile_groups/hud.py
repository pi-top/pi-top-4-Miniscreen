import logging
from typing import List

from ..event import AppEvent, subscribe
from ..tiles import HUDMenuTile, MenuTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class HUDTileGroup(TileGroup):
    def __init__(self, size):
        self.menu_tile_stack: List[MenuTile] = list()

        self.title_bar_height = 19
        root_menu_tile = HUDMenuTile(
            size=(size[0], size[1]),
            pos=(0, 0),
        )

        self.menu_tile_stack.append(root_menu_tile)

        def handle_go_to_child(menu_cls) -> None:
            self.current_menu_tile.active = False
            self.menu_tile_stack.append(
                MenuTile(
                    menu_cls=menu_cls,
                    size=(
                        size[0],
                        size[1],
                    ),
                    pos=(0, 0),
                )
            )
            self.current_menu_tile.active = True

        subscribe(AppEvent.GO_TO_CHILD_MENU, handle_go_to_child)

        super().__init__(size=size, menu_tile=root_menu_tile)

    @property
    def current_menu_tile(self):
        return self.menu_tile_stack[-1]

    def handle_cancel_btn(self) -> bool:
        if len(self.menu_tile_stack) == 1:
            return False

        self.menu_tile_stack.pop()
        self.current_menu_tile.active = True
        return True
