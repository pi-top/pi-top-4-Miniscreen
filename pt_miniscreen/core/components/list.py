import logging
import threading

from PIL import Image, ImageDraw

from ..component import Component
from ..utils import apply_layers, layer, rectangle, transition

logger = logging.getLogger(__name__)


class List(Component):
    transition_duration = 0.25

    def __init__(
        self,
        Rows,
        num_visible_rows=None,
        row_gap=0,
        scrollbar_width=10,
        scrollbar_border_width=1,
        scrollbar_vertical_padding=3,
        scrollbar_horizontal_padding=3,
        use_snapshot_when_scrolling=True,
        initial_state={},
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "num_visible_rows": len(Rows)
                if num_visible_rows is None
                else num_visible_rows,
                "row_gap": row_gap,
                "top_row_index": 0,
                "scrollbar_width": scrollbar_width,
                "scrollbar_border_width": scrollbar_border_width,
                "scrollbar_horizontal_padding": scrollbar_horizontal_padding,
                "scrollbar_vertical_padding": scrollbar_vertical_padding,
                "active_transition": None,
                "transition_progress": 0,
                **initial_state,
            },
        )

        self._visible = True
        self._rows_snap = None
        self._cancel_transition = threading.Event()
        self.use_snapshot_when_scrolling = use_snapshot_when_scrolling
        self.Rows = Rows
        self.rows = [
            self.create_child(Row) for Row in Rows[: self.state["num_visible_rows"]]
        ]

    def cleanup(self):
        self._cancel_transition.set()

    @property
    def visible_scrollbar(self):
        return self._visible

    @visible_scrollbar.setter
    def visible_scrollbar(self, value):
        self._visible = value

    @property
    def can_scroll_down(self):
        next_top_row_index = self.state["top_row_index"] + 1
        max_top_row_index = len(self.Rows) - self.state["num_visible_rows"]
        return next_top_row_index != max_top_row_index

    @property
    def can_scroll_up(self):
        return self.state["top_row_index"] > 0

    @property
    def visible_rows(self):
        if self.state["active_transition"] == "UP":
            return self.rows[: self.state["num_visible_rows"]]

        if self.state["active_transition"] == "DOWN":
            return self.rows[1:]

        return self.rows

    @property
    def _num_scroll_positions(self):
        total_rows = len(self.Rows)
        return total_rows - total_rows % self.state["num_visible_rows"]

    @property
    def _row_height(self):
        row_gap = self.state["row_gap"]
        num_visible_rows = self.state["num_visible_rows"]
        total_gap = max((num_visible_rows - 1) * row_gap, 0)
        return int((self.height - total_gap) / num_visible_rows)

    def _scroll_transition(self):
        for step in transition(
            distance=self.height,
            duration=self.transition_duration,
        ):
            if self._cancel_transition.is_set():
                return

            progress = self.state["transition_progress"]
            progress_step = step / self.height
            self.state.update({"transition_progress": progress + progress_step})

        active_transition = self.state["active_transition"]
        row_to_remove = self.rows[0 if active_transition == "DOWN" else -1]
        self.rows.remove(row_to_remove)
        self.remove_child(row_to_remove)
        self._rows_snap = None
        self.state.update({"active_transition": None, "transition_progress": 0})

    def scroll_up(self):
        if self.state["active_transition"] is not None:
            logger.debug(f"{self} currently scrolling, ignoring scroll up")
            return

        if not self.can_scroll_up:
            logger.debug(f"{self} has no more rows, ignoring scroll up")
            return

        next_top_row_index = self.state["top_row_index"] - 1
        Row = self.Rows[next_top_row_index]
        self.rows.insert(0, self.create_child(Row))

        self.state.update(
            {"active_transition": "UP", "top_row_index": next_top_row_index}
        )
        threading.Thread(target=self._scroll_transition).start()

    def scroll_down(self):
        if self.state["active_transition"] is not None:
            logger.debug(f"{self} currently scrolling, ignoring scroll down")
            return

        if not self.can_scroll_down:
            logger.debug(f"{self} has no more rows, ignoring scroll down")
            return

        next_top_row_index = self.state["top_row_index"] + 1
        Row = self.Rows[next_top_row_index + self.state["num_visible_rows"] - 1]
        self.rows.append(self.create_child(Row))

        self.state.update(
            {"active_transition": "DOWN", "top_row_index": next_top_row_index}
        )
        threading.Thread(target=self._scroll_transition).start()

    def _get_scrollbar_y(self, bar_height):
        bar_y = int(
            self.state["top_row_index"] * self.height / self._num_scroll_positions
        )

        # Offset the scrollbar according to transition progress.
        # Use the inverse of progress since offset decreases as it increases
        transition_progress = self.state["transition_progress"]

        if self.state["active_transition"] == "UP":
            return bar_y + int((1 - transition_progress) * bar_height)

        if self.state["active_transition"] == "DOWN":
            return bar_y - int((1 - transition_progress) * bar_height)

        return bar_y

    def _render_scrollbar(self, image):
        horizontal_padding = self.state["scrollbar_horizontal_padding"]
        vertical_padding = self.state["scrollbar_vertical_padding"]
        bar_height = int(image.height / self._num_scroll_positions)
        bar_y = self._get_scrollbar_y(bar_height)

        ImageDraw.Draw(image).rectangle(
            (
                horizontal_padding,
                bar_y + vertical_padding,
                image.size[0] - horizontal_padding,
                bar_y + bar_height - vertical_padding,
            ),
            fill="white",
        )
        return image

    def _render_rows(self, image):
        row_gap = self.state["row_gap"]
        row_height = self._row_height
        num_rows = len(self.rows)
        rows_height = row_height * num_rows + row_gap * (num_rows - 1)

        return apply_layers(
            Image.new("1", size=(image.width, rows_height)),
            [
                layer(
                    row.render,
                    size=(image.width, row_height),
                    pos=(0, (row_height + row_gap) * row_index),
                )
                for (row_index, row) in enumerate(self.rows)
            ],
        )

    def _render_rows_window(self, image):
        row_gap = self.state["row_gap"]
        row_height = self._row_height
        num_rows = len(self.rows)
        rows_height = row_height * num_rows + row_gap * (num_rows - 1)
        active_transition = self.state["active_transition"]

        # when there is no transition render all rows without cropping
        if not active_transition:
            return self._render_rows(image)

        # when a transition is active there is one extra row, the row that is
        # being scrolled into view. Crop the top row and bottom row according to
        # transition progress so the height of the visible rows remains the same
        progress = self.state["transition_progress"]
        progress_correction = (1 - progress) if active_transition == "UP" else progress

        offset_final = row_height + row_gap
        offset_top = int(offset_final * progress_correction)
        offset_bottom = rows_height - (offset_final - offset_top)

        if self.use_snapshot_when_scrolling:
            self._rows_snap = self._rows_snap or self._render_rows(image)
            return self._rows_snap.crop((0, offset_top, image.width, offset_bottom))

        return self._render_rows(image).crop(
            (0, offset_top, image.width, offset_bottom)
        )

    def render(self, image):
        scrollbar_width = self.state["scrollbar_width"]
        border_width = self.state["scrollbar_border_width"]
        pages_width = image.width - scrollbar_width - border_width

        # don't render scrollbar when all rows are visible
        if (
            not self.visible_scrollbar
            or len(self.Rows) <= self.state["num_visible_rows"]
        ):
            return self._render_rows(image)

        return apply_layers(
            image,
            [
                layer(
                    self._render_scrollbar,
                    size=(scrollbar_width - border_width, image.height),
                ),
                layer(
                    rectangle,
                    size=(border_width, image.height),
                    pos=(scrollbar_width, 0),
                ),
                layer(
                    self._render_rows_window,
                    size=(pages_width, image.height),
                    pos=(scrollbar_width + border_width, 0),
                ),
            ],
        )
