from pt_miniscreen.hotspots.menu_cover import MenuCoverHotspot
from pt_miniscreen.menus.settings import SettingsMenuHotspot
from pt_miniscreen.utils import get_image_file_path


class SettingsMenuCoverHotspot(MenuCoverHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            text="Settings",
            image_path=get_image_file_path("menu/settings.gif"),
            Menu=SettingsMenuHotspot,
            **kwargs
        )
