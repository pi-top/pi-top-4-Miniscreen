from ...menus import SettingsConnectionMenu
from ...utils import get_image_file_path
from ..templates.menu.page import Page as PageBase


class Page(PageBase):
    def __init__(self, size):
        super().__init__(
            size=size,
            image_path=get_image_file_path("menu/settings.gif"),
            text="Connection",
            child_menu_cls=SettingsConnectionMenu,
        )
