from ...utils import get_image_file_path
from ..templates.menu.page import Page as PageBase


class Page(PageBase):
    def __init__(self, size, mode):
        super().__init__(
            size=size,
            mode=mode,
            image_path=get_image_file_path("menu/settings.gif"),
            text="Connection",
        )
