import logging

from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.hotspots import PageList, Stack
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.action_page import ActionPage
from pt_miniscreen.hotspots.menu_page import MenuPage
from pt_miniscreen.hotspots.right_gutter import RightGutter
from pt_miniscreen.pages.root.network_menu import NetworkMenuPage
from pt_miniscreen.pages.root.overview import OverviewPage
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


# class DemoList(List):
#     transition_duration = 0.1

#     def __init__(self, **kwargs):
#         super().__init__(
#             **kwargs,
#             num_visible_rows=5,
#             scrollbar_vertical_padding=0,
#             row_gap=1,
#             Rows=[partial(IconTextRow, icon_path=get_image_file_path('sys_info/networking/home-small.png'), text="hello there")
#                   for _ in range(0, 100)]
#         )


class RootHotspot(Hotspot):
    right_gutter_width = 10
    gutter_icon_padding = (3, 7)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stack = self.create_hotspot(Stack, initial_stack=[RootPageList])
        self.right_gutter = self.create_hotspot(
            RightGutter,
            upper_icon_padding=self.gutter_icon_padding,
            lower_icon_padding=self.gutter_icon_padding,
        )

    @property
    def active_page(self):
        if isinstance(self.stack.active_hotspot, PageList):
            return self.stack.active_hotspot.current_page

    @property
    def can_enter_menu(self):
        return self.active_page and isinstance(self.active_page, MenuPage)

    @property
    def can_exit_menu(self):
        return self.stack.active_index > 0

    @property
    def can_scroll(self):
        return isinstance(self.stack.active_hotspot, PageList)

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
            self.stack.push(self.active_page.PageList)
            self._set_gutter_icons()

    def exit_menu(self):
        self.stack.pop()
        self._set_gutter_icons()

    def scroll_up(self):
        if self.can_scroll:
            self.stack.active_hotspot.scroll_up()
            self._set_gutter_icons()

    def scroll_down(self):
        if self.can_scroll:
            self.stack.active_hotspot.scroll_down()
            self._set_gutter_icons()

    def perform_action(self):
        if self.can_perform_action:
            self.active_page.perform_action()

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.stack.render,
                    size=(image.width - self.right_gutter_width, image.height),
                ),
                layer(
                    self.right_gutter.render,
                    size=(self.right_gutter_width, image.height),
                    pos=(image.size[0] - self.right_gutter_width, 0),
                ),
            ],
        )
