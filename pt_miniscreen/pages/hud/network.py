from ...menus import NetworkMenu
from ...utils import get_image_file_path
from ..templates.menu import Page as PageBase


class Page(PageBase):
    def __init__(self, size):
        super().__init__(
            size=size,
            text="Network",
            image_path=get_image_file_path("menu/network.gif"),
            child_menu_cls=NetworkMenu,
        )
