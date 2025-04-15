import logging
from functools import partial

from pt_miniscreen.components.right_gutter import RightGutter
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import PageList, Stack
from pt_miniscreen.components.mixins import (
    HasGutterIcons,
)
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.utils import ButtonEvents, get_image_file_path
from pt_miniscreen.welcome.text_page import TextPage

logger = logging.getLogger(__name__)


class RootPageList(PageList):
    def __init__(self, **kwargs):
        super().__init__(
            visible_scrollbar=False,
            virtual=False,
            Pages=[
                partial(
                    TextPage,
                    text="Welcome!\nPress 'O'\nto continue",
                    button_event=ButtonEvents.SELECT_RELEASE,
                    icons={"bottom": get_image_file_path("gutter/down_arrow.png")},
                ),
                partial(
                    TextPage,
                    text="Go to\npi-top.com/start\nPress 'X' to close",
                    button_event=ButtonEvents.CANCEL_RELEASE,
                    icons={
                        "top": get_image_file_path("gutter/cancel.png"),
                    },
                ),
            ],
            **kwargs,
        )


class WelcomeRootComponent(Component):
    right_gutter_width = 10
    gutter_icon_padding = (3, 7)

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            initial_state={
                "should_exit": False,
            },
        )

        self.stack = self.create_child(Stack, initial_stack=[RootPageList])
        self.right_gutter = self.create_child(
            RightGutter,
            upper_icon_padding=self.gutter_icon_padding,
            lower_icon_padding=self.gutter_icon_padding,
        )
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
    def can_scroll(self):
        return isinstance(self.active_component, PageList)

    @property
    def can_scroll_up(self):
        return self.can_scroll and self.active_component.can_scroll_up()

    @property
    def can_scroll_down(self):
        return self.can_scroll and self.active_component.can_scroll_down()

    @property
    def should_exit(self):
        return self.state["should_exit"]

    def scroll_up(self):
        if self.can_scroll_up:
            self.active_component.scroll_up()

    def scroll_down(self):
        if self.can_scroll_down:
            self.active_component.scroll_down()

    def _set_gutter_icons(self):
        if isinstance(self.active_page, HasGutterIcons):
            self.right_gutter.state.update(
                {
                    "upper_icon_path": self.active_page.top_gutter_icon(),
                    "lower_icon_path": self.active_page.bottom_gutter_icon(),
                }
            )

    def handle_button(
        self,
        button_event: ButtonEvents,
    ):
        try:
            if button_event != self.active_page.button_event:
                # button not handled by this page
                return

            if button_event == ButtonEvents.CANCEL_RELEASE:
                self.stack.pop()
                self.state.update({"should_exit": True})
                return

            if button_event == ButtonEvents.SELECT_RELEASE:
                self.active_component.scroll_down()
                return
        except Exception as e:
            logger.error(f"Error: {e}")
            if self.active_component is None:
                self.stack.pop()
        finally:
            self._set_gutter_icons()

    def render(self, image):
        if self.state["should_exit"]:
            return image

        if isinstance(self.active_page, HasGutterIcons):
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
