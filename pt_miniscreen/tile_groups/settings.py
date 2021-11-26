import logging

from ..event import AppEvents, post_event, subscribe
from ..tiles import SettingsMenuTile, SettingsTitleBarTile
from .base import TileGroup as TileGroupBase

logger = logging.getLogger(__name__)


class TileGroup(TileGroupBase):
    def __init__(
        self,
        size,
    ):

        title_bar_height = 19
        menu_tile = SettingsMenuTile(
            size=(size[0], size[1] - title_bar_height),
            pos=(0, title_bar_height),
        )

        title_bar_tile = SettingsTitleBarTile(
            size=(size[0], title_bar_height),
            pos=(0, 0),
        )

        def handle_go_to_child(menu_name):
            if not self.title_bar.append_title:
                return

            self.title_bar.text = (
                f"{self.title_bar.text}{self.title_bar.delimiter}{menu_name}"
            )

        def handle_go_to_parent():
            if not self.title_bar.append_title:
                return

            text_fields = self.title_bar.text.split(self.title_bar.delimiter)

            if len(text_fields) == 1:
                return

            self.title_bar.text = self.title_bar.delimiter.join(text_fields[:-1])

        # TODO - replace with callback?
        subscribe(AppEvents.GO_TO_CHILD_MENU, handle_go_to_child)
        subscribe(AppEvents.GO_TO_PARENT_MENU, handle_go_to_parent)

        super().__init__(size, menu_tile, title_bar_tile)

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        if self.menu_tile._current_page.child_menu:
            self.menu_tile._go_to_child_menu()
            return True
        elif False:
            post_event(AppEvents.BUTTON_ACTION_START)
            return True
        else:
            return False

    def handle_cancel_btn(self):
        # TODO: handle going back to parent
        # if MenuTileConfigManager.menu_id_has_parent(self.menu_tile.menus, self.menu_tile.menu_tile_id):
        # self.menu_tile.go_to_parent_menu()
        pass

    def handle_up_btn(self):
        self.menu_tile.set_page_to_previous()
        if self.menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_down_btn(self):
        self.menu_tile.set_page_to_next()
        if self.menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)
