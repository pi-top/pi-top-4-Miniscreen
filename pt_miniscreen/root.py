import logging
from configparser import ConfigParser
from os import path
from pathlib import Path
from threading import Thread

from pt_miniscreen.components.action_page import ActionPage
from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.components.right_gutter import RightGutter
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import PageList, Stack
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.pages.root.network_menu import NetworkMenuPage
from pt_miniscreen.pages.root.overview import OverviewPage
from pt_miniscreen.pages.root.projects import ProjectPage, ProjectsMenuPage
from pt_miniscreen.pages.root.screensaver import StarfieldScreensaver
from pt_miniscreen.pages.root.settings_menu import SettingsMenuPage
from pt_miniscreen.pages.root.system_menu import SystemMenuPage
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


def get_bootsplash_image_path():
    try:
        config = ConfigParser()
        config.read("/etc/pt-miniscreen/settings.ini")
        return config.get("Bootsplash", "Path")
    except Exception:
        pass

    return get_image_file_path("startup/pi-top_startup.gif")


class RootPageList(PageList):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            Pages=[
                OverviewPage,
                SystemMenuPage,
                NetworkMenuPage,
                ProjectsMenuPage,
                SettingsMenuPage,
            ],
        )


class RootComponent(Component):
    bootsplash_breadcrumb = "/tmp/.com.pi-top.pt_miniscreen.boot-played"
    right_gutter_width = 10
    gutter_icon_padding = (3, 7)

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            initial_state={
                "show_bootsplash": not path.exists(self.bootsplash_breadcrumb),
                "show_screensaver": False,
            },
        )

        self.stack = self.create_child(Stack, initial_stack=[RootPageList])
        self.right_gutter = self.create_child(
            RightGutter,
            upper_icon_padding=self.gutter_icon_padding,
            lower_icon_padding=self.gutter_icon_padding,
        )
        self.screensaver = self.create_child(StarfieldScreensaver)
        self.bootsplash = self.create_child(
            Image, loop=False, image_path=get_bootsplash_image_path()
        )

        if self.state["show_bootsplash"]:
            Thread(target=self._wait_for_bootsplash_finish, daemon=True).start()

    @property
    def active_page(self):
        if isinstance(self.stack.active_component, PageList):
            return self.stack.active_component.current_page
        elif isinstance(self.stack.active_component, ProjectPage):
            return self.stack.active_component

    @property
    def is_project_page(self):
        return self.active_page and isinstance(self.active_page, ProjectPage)

    @property
    def project_is_running(self):
        return self.active_page and isinstance(self.active_page, ProjectPage)

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
    def can_select_row(self):
        return isinstance(self.active_page, SelectableList)

    @property
    def can_perform_action(self):
        return isinstance(self.active_page, ActionPage)

    def _wait_for_bootsplash_finish(self):
        # wait for bootsplash animation to finish
        self.bootsplash.stop_animating_event.wait(10)

        # try to create breadcrumb so the bootsplash is not shown next start
        try:
            Path(self.bootsplash_breadcrumb).touch()
        except Exception:
            pass

        # start showing main app
        self.state.update({"show_bootsplash": False})

    def _get_upper_icon_path(self):
        if self.can_exit_menu:
            return get_image_file_path("gutter/left_arrow.png")

        if self.stack.active_component.can_scroll_up():
            return get_image_file_path("gutter/top_arrow.png")

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

    def enter_selected_row(self):
        if self.can_select_row and self.active_page.selected_row.page:
            self.stack.push(self.active_page.selected_row.page)
            self._set_gutter_icons()

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

    def select_next_row(self):
        if self.can_select_row:
            self.active_page.select_next_row()

    def select_previous_row(self):
        if self.can_select_row:
            self.active_page.select_previous_row()

    def start_project(self):
        if self.is_project_page:
            return self.active_page.start()

    def handle_cancel_button_release(self):
        if self.is_project_page:
            return

        if self.can_exit_menu:
            return self.exit_menu()

        self.stack.active_component.scroll_to_top()
        self._set_gutter_icons()

    def perform_action(self):
        if self.can_perform_action:
            self.active_page.perform_action()

    def start_screensaver(self):
        self.state.update({"show_screensaver": True})

    def stop_screensaver(self):
        self.state.update({"show_screensaver": False})

    @property
    def is_screensaver_running(self):
        return self.state["show_screensaver"]

    def on_state_change(self, previous_state):
        show_screensaver = self.state["show_screensaver"]
        prev_show_screensaver = previous_state["show_screensaver"]

        if show_screensaver and not prev_show_screensaver:
            self.screensaver.start_animating()

        if not show_screensaver and prev_show_screensaver:
            self.screensaver.stop_animating()

    def render(self, image):
        if self.state["show_bootsplash"]:
            return self.bootsplash.render(image)

        if self.is_screensaver_running:
            return self.screensaver.render(image)

        if self.is_project_page:
            return self.stack.render(image)

        return apply_layers(
            image,
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
            ),
        )
