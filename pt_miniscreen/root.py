import logging

from pt_miniscreen.components.action_page import ActionPage
from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.components.right_gutter import RightGutter
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import PageList, Stack
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.pages.root.network_menu import NetworkMenuPage
from pt_miniscreen.pages.root.overview import OverviewPage
from pt_miniscreen.pages.root.screensaver import StarfieldScreensaver
from pt_miniscreen.pages.root.settings_menu import SettingsMenuPage
from pt_miniscreen.pages.root.system_menu import SystemMenuPage
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class RootPageList(PageList):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            Pages=[
                OverviewPage,
                SystemMenuPage,
                NetworkMenuPage,
                SettingsMenuPage,
            ],
        )


class RootComponent(Component):
    right_gutter_width = 10
    gutter_icon_padding = (3, 7)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stack = self.create_child(Stack, initial_stack=[RootPageList])
        self.right_gutter = self.create_child(
            RightGutter,
            upper_icon_padding=self.gutter_icon_padding,
            lower_icon_padding=self.gutter_icon_padding,
        )

    @property
    def active_page(self):
        if isinstance(self.stack.active_component, PageList):
            return self.stack.active_component.current_page

    @property
    def can_enter_menu(self):
        return self.active_page and isinstance(self.active_page, MenuPage)

    @property
    def can_exit_menu(self):
        return self.stack.active_index > 0

    @property
    def can_scroll(self):
        return isinstance(self.stack.active_component, PageList)

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
        self.right_gutter.state.update(
            {
                "upper_icon_path": self._get_upper_icon_path(),
                "lower_icon_path": self._get_lower_icon_path(),
            }
        )

    def enter_menu(self):
        if self.can_enter_menu:
            self.stack.push(self.active_page.PageList)
            self._set_gutter_icons()

    def exit_menu(self):
        if self.can_exit_menu:
            self.stack.pop()
            self._set_gutter_icons()

    def scroll_up(self):
        if self.can_scroll:
            self.stack.active_component.scroll_up()
            self._set_gutter_icons()

    def scroll_down(self):
        if self.can_scroll:
            self.stack.active_component.scroll_down()
            self._set_gutter_icons()

    def perform_action(self):
        if self.can_perform_action:
            self.active_page.perform_action()

    def start_screensaver(self):
        if not self.is_screensaver_running:
            self.stack.push(StarfieldScreensaver)

    def stop_screensaver(self):
        if self.is_screensaver_running:
            self.stack.pop()

    @property
    def is_screensaver_running(self):
        return isinstance(self.stack.active_component, StarfieldScreensaver)

    def render(self, image):
        layer_arr = []
        if self.is_screensaver_running:
            layer_arr.append(
                layer(
                    self.stack.render,
                    size=(image.width, image.height),
                )
            )
        else:
            layer_arr.extend(
                (
                    layer(
                        self.stack.render,
                        size=(image.width - self.right_gutter_width, image.height),
                    ),
                    layer(
                        self.right_gutter.render,
                        size=(self.right_gutter_width, image.height),
                        pos=(image.size[0] - self.right_gutter_width, 0),
                    ),
                )
            )

        return apply_layers(image, layer_arr)
