from pt_miniscreen.hotspots.menu_cover import MenuCoverHotspot
from pt_miniscreen.menus.system import SystemMenuHotspot
from pt_miniscreen.utils import get_image_file_path


class SystemMenuCoverHotspot(MenuCoverHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            text="System",
            image_path=get_image_file_path("menu/system.gif"),
            image_size=(29, 29),
            Menu=SystemMenuHotspot,
            **kwargs
        )
