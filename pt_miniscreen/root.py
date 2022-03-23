import logging

from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.hotspots import NavigationControllerHotspot, PaginatedHotspot
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.action_page import ActionPage
from pt_miniscreen.hotspots.menu_cover import MenuCoverHotspot
from pt_miniscreen.hotspots.right_gutter import RightGutterHotspot
from pt_miniscreen.menus.hud import HUDMenuHotspot
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class RootHotspot(Hotspot):
    right_gutter_width = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        gutter_icon_padding = (3, 7)
        self.right_gutter = self.create_hotspot(
            RightGutterHotspot,
            upper_icon_padding=gutter_icon_padding,
            lower_icon_padding=gutter_icon_padding,
        )
        self.navigation_controller = self.create_hotspot(
            NavigationControllerHotspot, initial_stack=[HUDMenuHotspot]
        )

    @property
    def active_page(self):
        if isinstance(self.navigation_controller.active_hotspot, PaginatedHotspot):
            return self.navigation_controller.active_hotspot.current_page

    @property
    def can_enter_menu(self):
        return self.active_page and isinstance(self.active_page, MenuCoverHotspot)

    @property
    def can_exit_menu(self):
        return self.navigation_controller.active_index > 0

    @property
    def can_scroll(self):
        return isinstance(self.navigation_controller.active_hotspot, PaginatedHotspot)

    @property
    def can_perform_action(self):
        return isinstance(self.active_page, ActionPage)

    def _get_upper_icon_path(self):
        if self.can_exit_menu:
            return get_image_file_path("gutter/left_arrow.png")

    def _get_lower_icon_path(self):
        if self.can_perform_action:
            return get_image_file_path("gutter/tick.png")

        if self.can_enter_menu:
            return get_image_file_path("gutter/right_arrow.png")

    def _set_gutter_icons(self):
        self.right_gutter.upper_icon.state.update(
            {"image_path": self._get_upper_icon_path()}
        )
        self.right_gutter.lower_icon.state.update(
            {"image_path": self._get_lower_icon_path()}
        )

    def enter_menu(self):
        if self.can_enter_menu:
            self.navigation_controller.push(self.active_page.Menu)
            self._set_gutter_icons()

    def exit_menu(self):
        self.navigation_controller.pop()
        self._set_gutter_icons()

    def scroll_up(self):
        if self.can_scroll:
            self.navigation_controller.active_hotspot.scroll_up()
            self._set_gutter_icons()

    def scroll_down(self):
        if self.can_scroll:
            self.navigation_controller.active_hotspot.scroll_down()
            self._set_gutter_icons()

    def perform_action(self):
        if self.can_perform_action:
            self.active_page.perform_action()

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.navigation_controller.render,
                    size=(image.width - self.right_gutter_width, image.height),
                ),
                layer(
                    self.right_gutter.render,
                    size=(self.right_gutter_width, image.height),
                    pos=(image.size[0] - self.right_gutter_width, 0),
                ),
            ],
        )
