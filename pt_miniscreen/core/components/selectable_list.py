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
                "selected_index": 0,
                **initial_state,
            },
        )

        self._selected_row_unmodified_render = None
        if len(self.rows) != 0:
            self._selected_row_unmodified_render = self.selected_row.render
            self.selected_row.render = lambda image: ImageOps.invert(
                self._selected_row_unmodified_render(image).convert("L")
            ).convert("1")

    @property
    def selected_row(self):
        return self._get_row_at_index(self.state["selected_index"])

    @property
    def is_empty(self):
        return len(self.rows) == 0

    def select_row(self, index, animate_scroll=True):
        if self.state["active_transition"] is not None:
            logger.info(f"{self} selecting new row, ignoring select")
            return

        if 0 > index or index >= len(self.state["Rows"]):
            logger.info(
                f"select_row: Invalid index {index}, should be in range 0 - {len(self.state['Rows']) - 1}"
            )
            return

        offset = index - self.state["top_row_index"]
        if offset < 0:
            self.scroll_to(direction="UP", distance=-offset, animate=animate_scroll)
        elif offset >= self.state["num_visible_rows"]:
            self.scroll_to(
                direction="DOWN",
                distance=1 + offset - self.state["num_visible_rows"],
                animate=animate_scroll,
            )

        self.state.update({"selected_index": index})

    def select_next_row(self, animate_scroll=True):
        self.select_row(self.state["selected_index"] + 1, animate_scroll=animate_scroll)

    def select_previous_row(self, animate_scroll=True):
        self.select_row(self.state["selected_index"] - 1, animate_scroll=animate_scroll)

    def _get_row_at_index(self, index):
        if len(self.rows) == 0:
            return None

        if not self._virtual:
            return self.rows[index]

        if self.state["active_transition"] == "DOWN":
            return self.rows[
                index - self.state["top_row_index"] + self.state["transition_distance"]
            ]

        return self.rows[index - self.state["top_row_index"]]

    def on_state_change(self, previous_state):
        if previous_state["selected_index"] != self.state["selected_index"]:
            previous_row = self._get_row_at_index(previous_state["selected_index"])
            previous_row.render = self._selected_row_unmodified_render

            self._selected_row_unmodified_render = self.selected_row.render
            self.selected_row.render = lambda image: ImageOps.invert(
                self._selected_row_unmodified_render(image).convert("L")
            ).convert("1")

        return super().on_state_change(previous_state)
