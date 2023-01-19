import logging
from typing import Callable, Optional

from pt_miniscreen.components.mixins import (
    Actionable,
    Enterable,
    HandlesButtonEvents,
    HasGutterIcons,
)
from pt_miniscreen.core.components.page_list import PageList
from pt_miniscreen.core.components.stack import Stack
from pt_miniscreen.utils import ButtonEvents, get_image_file_path


logger = logging.getLogger(__name__)


class ButtonNavigablePageList(PageList, HandlesButtonEvents, Enterable, HasGutterIcons):
    def __init__(
        self,
        Pages,
        num_visible_rows=None,  # take num_visible_rows out of kwargs
        row_gap=None,  # take row_gap out of kwargs
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            Pages=Pages,
            num_visible_rows=1,
            row_gap=0,
        )

    def handle_button(
        self,
        button_event: ButtonEvents,
        callback: Optional[Callable],
        **kwargs,
    ) -> None:
        if button_event == ButtonEvents.UP_RELEASE:
            self.scroll_up()
        elif button_event == ButtonEvents.DOWN_RELEASE:
            self.scroll_down()
        elif button_event == ButtonEvents.CANCEL_RELEASE:
            stack = kwargs.get("stack")
            if isinstance(stack, Stack) and len(stack.stack) > 1:
                self.exit(stack, None)
            else:
                self.scroll_to_top()
        elif button_event == ButtonEvents.SELECT_RELEASE:
            if isinstance(self.current_page, Actionable):
                self.current_page.perform_action()
            else:
                self.enter(kwargs.get("stack"), None)
        else:
            return

        if callable(callback):
            callback()

    @property
    def enterable_component(self):
        if isinstance(self.current_page, Enterable):
            return self.current_page.enterable_component
        return None

    def top_gutter_icon(self, **kwargs):
        stack = kwargs.get("stack")
        if isinstance(stack, Stack) and len(stack.stack) > 1:
            return get_image_file_path("gutter/left_arrow.png")

        if self.can_scroll_up():
            return get_image_file_path("gutter/top_arrow.png")

    def bottom_gutter_icon(self, **kwargs):
        if isinstance(self.current_page, Actionable):
            return get_image_file_path("gutter/tick.png")

        if isinstance(self.current_page, Enterable):
            return get_image_file_path("gutter/right_arrow.png")
