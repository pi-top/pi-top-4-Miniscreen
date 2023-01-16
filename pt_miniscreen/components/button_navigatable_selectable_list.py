from typing import Callable, Optional
from pt_miniscreen.components.mixins import (
    Actionable,
    Enterable,
    HandlesButtonEvents,
    HasGutterIcons,
)
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.core.components.stack import Stack
from pt_miniscreen.utils import ButtonEvents, get_image_file_path


class ButtonNavigatableSelectableList(
    SelectableList, HandlesButtonEvents, Enterable, HasGutterIcons
):
    def __init__(
        self,
        Rows,
        num_visible_rows=5,
        **kwargs,
    ) -> None:
        super().__init__(
            Rows=Rows,
            num_visible_rows=num_visible_rows,
            **kwargs,
        )

    @property
    def can_enter(self) -> bool:
        return isinstance(self.selected_row, Enterable)

    @property
    def enterable_component(self):
        return self.selected_row.page if self.can_enter else None

    def enter(self, stack: Stack, on_enter: Optional[Callable]) -> None:
        if self.can_enter:
            super().enter(stack, on_enter)

    def handle_button(
        self,
        button_event: ButtonEvents,
        callback: Optional[Callable],
        **kwargs,
    ) -> None:
        if button_event == ButtonEvents.UP_RELEASE:
            self.select_previous_row()
        elif button_event == ButtonEvents.DOWN_RELEASE:
            self.select_next_row()
        elif button_event == ButtonEvents.SELECT_RELEASE:
            self.enter(kwargs.get("stack"), None)
        elif button_event == ButtonEvents.CANCEL_RELEASE:
            self.exit(kwargs.get("stack"), None)
        else:
            return

        if callable(callback):
            callback()

    def top_gutter_icon(self, stack: Stack):
        if len(stack.stack) > 1:
            return get_image_file_path("gutter/left_arrow.png")

        if self.can_select_previous:
            return get_image_file_path("gutter/top_arrow.png")

    def bottom_gutter_icon(self):
        if isinstance(self.selected_row.enterable_component, Actionable):
            return get_image_file_path("gutter/tick.png")

        if self.can_enter:
            return get_image_file_path("gutter/right_arrow.png")
