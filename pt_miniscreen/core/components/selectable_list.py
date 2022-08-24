import logging

from PIL import ImageOps

from .list import List

logger = logging.getLogger(__name__)


class SelectableList(List):
    def __init__(
        self,
        initial_state={},
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "num_visible_rows": 5,
                "selected_index": 0,
                **initial_state,
            },
        )
        self._selected_row_unmodified_render = self.selected_row.render
        self.selected_row.render = lambda image: ImageOps.invert(
            self._selected_row_unmodified_render(image).convert("L")
        ).convert("1")

    @property
    def selected_row(self):
        return self.rows[self.state["selected_index"]]

    def select_row(self, index):
        if self.state["active_transition"] is not None:
            logger.info(f"{self} selecting new row, ignoring select")
            return

        if 0 > index or index >= len(self.rows):
            logger.error(
                f"select_row: Invalid index {index}, should be in range 0 - {len(self.rows) - 1}"
            )
            return

        offset = index - self.state["top_row_index"]
        if offset < 0:
            self.scroll_to(direction="UP", distance=-offset)
        elif offset >= self.state["num_visible_rows"]:
            self.scroll_to(
                direction="DOWN", distance=1 + offset - self.state["num_visible_rows"]
            )

        self.state.update({"selected_index": index})

    def select_next_row(self):
        self.select_row(self.state["selected_index"] + 1)

    def select_previous_row(self):
        self.select_row(self.state["selected_index"] - 1)

    def on_state_change(self, previous_state):
        if previous_state["selected_index"] != self.state["selected_index"]:
            self.rows[
                previous_state["selected_index"]
            ].render = self._selected_row_unmodified_render
            self._selected_row_unmodified_render = self.selected_row.render
            self.selected_row.render = lambda image: ImageOps.invert(
                self._selected_row_unmodified_render(image).convert("L")
            ).convert("1")
        return super().on_state_change(previous_state)
