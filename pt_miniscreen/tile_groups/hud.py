import logging
from typing import List

from pt_miniscreen.tiles.right_gutter import RightGutterTile

from ..event import AppEvent, subscribe
from ..tiles import MenuTile
from ..tiles.menu.hud import HUDMenuTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class HUDTileGroup(TileGroup):
    def __init__(self, size):
        self.right_gutter_width = 10
        self.right_gutter_tile = RightGutterTile(
            size=(self.right_gutter_width, size[1]),
            pos=(size[0] - self.right_gutter_width, 0),
        )

        root_menu_tile = HUDMenuTile(
            size=(size[0] - self.right_gutter_width, size[1]),
            pos=(0, 0),
        )
        self.menu_tile_stack: List[MenuTile] = list()
        self.menu_tile_stack.append(root_menu_tile)

        subscribe(AppEvent.SCROLL_START, self.set_gutter_icons)
        subscribe(AppEvent.GO_TO_CHILD_MENU, self.handle_go_to_child)

        super().__init__(size=size, menu_tile=root_menu_tile)

    def set_gutter_icons(self):
        self.right_gutter_tile.set_left_arrow_visible(len(self.menu_tile_stack) > 1)

        self.right_gutter_tile.set_tick_visible(
            hasattr(self.current_menu_tile.current_page, "action_state")
        )

        self.right_gutter_tile.set_right_arrow_visible(
            self.current_menu_tile.current_page.child_menu_cls is not None
        )

    def handle_go_to_child(self, ChildMenuTile) -> None:
        previous_menu_tile = self.current_menu_tile
        self.menu_tile_stack.append(ChildMenuTile(size=self.size, pos=(0, 0)))
        previous_menu_tile.active = False
        self.current_menu_tile.active = True
        self.set_gutter_icons()

    @property
    def current_menu_tile(self):
        return self.menu_tile_stack[-1]

    def handle_cancel_btn(self) -> bool:
        if len(self.menu_tile_stack) == 1:
            return False

        self.menu_tile_stack.pop()
        self.set_gutter_icons()
        self.current_menu_tile.active = True
        return True

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, is_active: bool) -> None:
        self._active = is_active
        self.current_menu_tile.active = is_active
        self.right_gutter_tile.active = is_active

    @property
    def image(self):
        # get image from super
        image = super().image

        # paste right gutter in
        image.paste(self.right_gutter_tile.image, self.right_gutter_tile.pos)

        return image
