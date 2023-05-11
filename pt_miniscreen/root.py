import logging
from configparser import ConfigParser
from os import path
from pathlib import Path
from threading import Thread

from pt_miniscreen.components.enterable_page_list import (
    EnterablePageList,
)
from pt_miniscreen.components.right_gutter import RightGutter
from pt_miniscreen.components.scrollable import Scrollable
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import PageList, Stack
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.components.mixins import (
    Actionable,
    BlocksMiniscreenButtons,
    Enterable,
    Navigable,
    HasGutterIcons,
    Poppable,
)
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.pages.root.network_menu import NetworkMenuPage
from pt_miniscreen.pages.root.overview import OverviewPage
from pt_miniscreen.pages.root.projects import (
    ProjectsMenuPage,
    ProjectPage,
)
from pt_miniscreen.pages.root.screensaver import StarfieldScreensaver
from pt_miniscreen.pages.root.settings_menu import SettingsMenuPage
from pt_miniscreen.pages.root.system_menu import SystemMenuPage
from pt_miniscreen.utils import ButtonEvents, get_image_file_path

logger = logging.getLogger(__name__)


def get_bootsplash_image_path():
    try:
        config = ConfigParser()
        config.read("/etc/pt-miniscreen/settings.ini")
        return config.get("Bootsplash", "Path")
    except Exception:
        pass

    return get_image_file_path("startup/pi-top_startup.gif")


class RootPageList(EnterablePageList):
    def __init__(self, **kwargs):
        super().__init__(
            Pages=[
                OverviewPage,
                SystemMenuPage,
                NetworkMenuPage,
                ProjectsMenuPage,
                SettingsMenuPage,
            ],
            use_snapshot_when_scrolling=False,
            **kwargs,
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

        self._set_gutter_icons()

    @property
    def active_component(self):
        return self.stack.active_component

    @property
    def active_page(self):
        if isinstance(self.active_component, PageList):
            return self.active_component.current_page
        return None

    @property
    def is_project_page(self):
        return isinstance(self.active_component, ProjectPage)

    def project_uses_miniscreen(self, user_using_miniscreen):
        if self.is_project_page:
            self.active_component.set_user_controls_miniscreen(user_using_miniscreen)
        return None

    @property
    def can_enter(self):
        return isinstance(self.active_component, Enterable)

    @property
    def can_exit(self):
        active_index = self.stack.active_index
        return False if active_index is None else active_index > 0

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

    def _set_gutter_icons(self):
        if isinstance(self.active_component, HasGutterIcons):

            def top_gutter_icon():
                if self.stack.active_index != 0:
                    return get_image_file_path("gutter/left_arrow.png")
                return self.active_component.top_gutter_icon()

            self.right_gutter.state.update(
                {
                    "upper_icon_path": top_gutter_icon(),
                    "lower_icon_path": self.active_component.bottom_gutter_icon(),
                }
            )

    def handle_button(
        self,
        button_event: ButtonEvents,
    ):
        try:
            if (
                isinstance(self.active_component, BlocksMiniscreenButtons)
                and self.active_component.block_buttons
            ):
                return

            if button_event == ButtonEvents.CANCEL_RELEASE and self.can_exit:
                self.stack.pop()
                return

            if isinstance(self.active_page, Actionable):
                if button_event == ButtonEvents.SELECT_RELEASE:
                    self.active_page.perform_action()
                    return

            if isinstance(self.active_component, Actionable):
                if button_event == ButtonEvents.SELECT_RELEASE:
                    self.active_component.perform_action()
                    return

            if isinstance(self.active_component, Enterable):
                if button_event == ButtonEvents.SELECT_RELEASE:
                    component = self.active_component.enterable_component
                    if component is None:
                        return

                    self.stack.push(component)

                    # Check that the instantiated component (not the partial) is Poppable
                    if isinstance(self.active_component, Poppable):
                        self.active_component.set_pop(self.stack.pop)

                    return

            if isinstance(self.active_component, Navigable):
                if button_event == ButtonEvents.UP_RELEASE:
                    self.active_component.go_previous()
                    return

                if button_event == ButtonEvents.DOWN_RELEASE:
                    self.active_component.go_next()
                    return

                if button_event == ButtonEvents.CANCEL_RELEASE:
                    self.active_component.go_top()
                    return

            if isinstance(self.active_component, Scrollable):
                if button_event == ButtonEvents.UP_PRESS:
                    self.active_component.scroll_up()
                    return

                if button_event == ButtonEvents.DOWN_PRESS:
                    self.active_component.scroll_down()
                    return

                if button_event in (ButtonEvents.DOWN_RELEASE, ButtonEvents.UP_RELEASE):
                    self.active_component.stop_scrolling()
                    return

        except Exception as e:
            logger.error(f"Error: {e}")
            if self.active_component is None:
                self.stack.pop()
        finally:
            self._set_gutter_icons()

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

        if isinstance(self.active_component, HasGutterIcons):
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

        return self.stack.render(image)
