from ...utils import get_image_file_path
from ..templates.menu import Page as PageBase


class Page(PageBase):
    def __init__(self, size, mode, config):
        super().__init__(
            size=size,
            mode=mode,
            config=config,
            image_path=get_image_file_path("menu/settings.gif"),
            text="Display",
        )
