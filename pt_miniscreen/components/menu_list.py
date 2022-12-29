from functools import partial
from pt_miniscreen.core.components.selectable_list import SelectableList


class MenuList(SelectableList):
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
    def can_enter(self):
        return hasattr(self.selected_row, "page") and self.selected_row.page is not None

    @property
    def child(self):
        if self.can_enter:
            return self.selected_row.page

    @property
    def child_cls(self):
        if isinstance(self.child, partial):
            return self.child.func
        return self.child
