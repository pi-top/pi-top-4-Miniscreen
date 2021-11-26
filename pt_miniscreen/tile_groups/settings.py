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
            if not title_bar_tile.append_title:
                return

            title_bar_tile.text = (
                f"{title_bar_tile.text}{title_bar_tile.delimiter}{menu_name}"
            )

        def handle_go_to_parent(_):
            if not title_bar_tile.append_title:
                return

            text_fields = title_bar_tile.text.split(title_bar_tile.delimiter)

            if len(text_fields) == 1:
                return

            title_bar_tile.text = title_bar_tile.delimiter.join(text_fields[:-1])

        # TODO - replace with callback?
        subscribe(AppEvents.GO_TO_CHILD_MENU, handle_go_to_child)
        subscribe(AppEvents.GO_TO_PARENT_MENU, handle_go_to_parent)

        super().__init__(size, menu_tile, title_bar_tile)

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        if self.current_menu_tile.current_page.child_menu:
            self.current_menu_tile.go_to_child_menu()
            return True
        elif False:
            post_event(AppEvents.BUTTON_ACTION_START)
            return True
        else:
            return False

    def handle_cancel_btn(self):
        if len(self.menu_tiles) > 1:
            self.current_menu_tile.go_to_parent_menu()
            return True
        return False

    def handle_up_btn(self):
        self.current_menu_tile.set_page_to_previous()
        if self.current_menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_down_btn(self):
        self.current_menu_tile.set_page_to_next()
        if self.current_menu_tile.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)
