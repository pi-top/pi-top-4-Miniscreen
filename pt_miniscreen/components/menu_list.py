from typing import Optional
from pt_miniscreen.core.component import Component
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
    def can_enter(self) -> bool:
        return hasattr(self.selected_row, "page") and self.selected_row.page is not None

    @property
    def child(self) -> Optional[Component]:
        return self.selected_row.page if self.can_enter else None
