import logging

from ..event import AppEvents, subscribe
from ..tiles import SettingsMenuTile, SettingsTitleBarTile
from .base import TileGroup

logger = logging.getLogger(__name__)


class SettingsTileGroup(TileGroup):
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

        def handle_go_to_child(menu_cls):
            if not title_bar_tile.append_title:
                return

            title_bar_tile.text = (
                f"{title_bar_tile.text}{title_bar_tile.delimiter}{menu_cls.name}"
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
