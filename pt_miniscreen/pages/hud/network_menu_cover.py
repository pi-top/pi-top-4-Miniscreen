from pt_miniscreen.hotspots.menu_cover import MenuCoverHotspot
from pt_miniscreen.menus.network import NetworkMenuHotspot
from pt_miniscreen.utils import get_image_file_path


class NetworkMenuCoverHotspot(MenuCoverHotspot):
    def __init__(self, **kwargs):
        super().__init__(
            text="Network",
            image_path=get_image_file_path("menu/network.gif"),
            Menu=NetworkMenuHotspot,
            **kwargs
        )
