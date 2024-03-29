from pt_miniscreen.components.mixins import (
    Actionable,
    Enterable,
    Navigable,
    HasGutterIcons,
)
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.utils import get_image_file_path


class EnterableSelectableList(SelectableList, Navigable, Enterable, HasGutterIcons):
    def __init__(
        self,
        Rows,
        num_visible_rows=5,
        **kwargs,
    ) -> None:
        SelectableList.__init__(
            self,
            Rows=Rows,
            num_visible_rows=num_visible_rows,
            **kwargs,
        )

    @property
    def can_enter(self) -> bool:
        return isinstance(self.selected_row, Enterable)

    @property
    def enterable_component(self):
        return (
            self.selected_row.enterable_component
            if self.can_enter
            else self.selected_row
        )

    def top_gutter_icon(self):
        if self.can_select_previous:
            return get_image_file_path("gutter/top_arrow.png")
        return None

    def bottom_gutter_icon(self):
        # If selected row is Enterable, check if the component we'll
        # be moving into is Actionable to display the tick icon
        if isinstance(self.selected_row, Enterable) and isinstance(
            self.selected_row.enterable_component, Actionable
        ):
            return get_image_file_path("gutter/tick.png")

        if self.can_enter:
            return get_image_file_path("gutter/right_arrow.png")

        return None

    def go_next(self):
        return self.select_next_row()

    def go_previous(self):
        return self.select_previous_row()

    def go_top(self):
        pass
