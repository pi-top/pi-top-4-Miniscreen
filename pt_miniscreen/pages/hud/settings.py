from ...tiles.menu.settings import SettingsMenuTile
from ...utils import get_image_file_path
from ..templates.menu import Page as PageBase


class Page(PageBase):
    def __init__(self, size):
        super().__init__(
            size=size,
            image_path=get_image_file_path("menu/settings.gif"),
            text="Settings",
            child_menu_cls=SettingsMenuTile,
        )
