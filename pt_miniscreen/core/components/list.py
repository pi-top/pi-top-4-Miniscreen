import logging
import threading
from math import ceil

from PIL import Image, ImageDraw

from ..component import Component
from ..utils import apply_layers, layer, rectangle, transition

logger = logging.getLogger(__name__)


class List(Component):
    def cleanup(self):
        if hasattr(self, "_cleanup_transition"):
            self._cleanup_transition.set()

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
        transition_duration=0.25,
        initial_top_row_index=0,
        visible_scrollbar=True,
        initial_state={},
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "Rows": Rows,
                "num_visible_rows": len(Rows)
                if num_visible_rows is None
                else num_visible_rows,
                "row_gap": row_gap,
                "top_row_index": initial_top_row_index,
                "scrollbar_width": scrollbar_width,
                "scrollbar_border_width": scrollbar_border_width,
                "scrollbar_horizontal_padding": scrollbar_horizontal_padding,
                "scrollbar_vertical_padding": scrollbar_vertical_padding,
                "active_transition": None,
                "transition_progress": 0,
                "transition_duration": transition_duration,
                "use_snapshot_when_scrolling": use_snapshot_when_scrolling,
                "visible_scrollbar": visible_scrollbar,
                **initial_state,
            },
        )

        self._rows_snapshot = None
        self._cleanup_transition = threading.Event()

        # setup initial rows
        start_index = self.state["top_row_index"]
        end_index = self.state["num_visible_rows"] + self.state["top_row_index"]
        self.rows = [self.create_child(Row) for Row in Rows[start_index:end_index]]

    @property
    def visible_scrollbar(self):
        return self.state["visible_scrollbar"]

    @visible_scrollbar.setter
    def visible_scrollbar(self, value):
        self.state.update({"visible_scrollbar": value})

    @property
    def distance_to_bottom(self):
        max_top_row_index = len(self.state["Rows"]) - self.state["num_visible_rows"]
        return max_top_row_index - self.state["top_row_index"]

    @property
    def distance_to_top(self):
        return self.state["top_row_index"]

    def can_scroll_down(self, distance=1):
        next_top_row_index = self.state["top_row_index"] + distance
        max_top_row_index = len(self.state["Rows"]) - self.state["num_visible_rows"]
        return next_top_row_index <= max_top_row_index

    def can_scroll_up(self, distance=1):
        return self.state["top_row_index"] + 1 > distance

    @property
    def visible_rows(self):
        if self.state["active_transition"] == "UP":
            return self.rows[: self.state["num_visible_rows"]]

        if self.state["active_transition"] == "DOWN":
            return self.rows[1:]

        return self.rows

    def _scroll_transition(self, distance):
        # only animate transition if we know our height
        # use height for distance since that is the max possible distance
        if self.height:
            for step in transition(
                distance=self.height * distance,
                duration=self.state["transition_duration"],
            ):
                if self._cleanup_transition.is_set():
                    return

                progress = self.state["transition_progress"]
                progress_step = step / self.height
                self.state.update({"transition_progress": progress + progress_step})

        active_transition = self.state["active_transition"]
        rows_to_remove = self.rows[-distance:]
        if active_transition == "DOWN":
            rows_to_remove = self.rows[:distance]

        for row in rows_to_remove:
            self.rows.remove(row)
            self.remove_child(row)
        self._rows_snapshot = None
        self.state.update({"active_transition": None, "transition_progress": 0})

    def scroll_to(self, direction, distance=1):
        if self.state["active_transition"] is not None:
            logger.info(f"{self} currently scrolling, ignoring scroll")
            return

        if direction == "UP":
            if not self.can_scroll_up(distance):
                return

            for i in range(distance):
                next_top_row_index = self.state["top_row_index"] - (i + 1)
                Row = self.state["Rows"][next_top_row_index]
                self.rows.insert(0, self.create_child(Row))
        elif direction == "DOWN":
            if not self.can_scroll_down(distance):
                return

            for i in range(distance):
                next_top_row_index = self.state["top_row_index"] + (i + 1)
                Row = self.state["Rows"][
                    next_top_row_index + self.state["num_visible_rows"] - 1
                ]
                self.rows.append(self.create_child(Row))

        self.state.update(
            {"active_transition": direction, "top_row_index": next_top_row_index}
        )
        threading.Thread(target=self._scroll_transition, args=(distance,)).start()

    def scroll_up(self, distance=1):
        self.scroll_to(direction="UP", distance=distance)

    def scroll_down(self, distance=1):
        self.scroll_to(direction="DOWN", distance=distance)

    def _get_row_height(self):
        # height is 0 if there are no rows
        num_visible_rows = self.state["num_visible_rows"]
        if num_visible_rows == 0:
            return 0

        row_gap = self.state["row_gap"]
        total_gap = max((num_visible_rows - 1) * row_gap, 0)
        return ceil((self.height - total_gap) / num_visible_rows)

    def _get_rows_height(self):
        row_height = self._get_row_height()
        row_gap = self.state["row_gap"]
        num_rows = len(self.rows)
        num_row_gaps = max(num_rows - 1, 0)
        return row_height * num_rows + row_gap * num_row_gaps

    def _get_scrollbar_y(self):
        Rows = self.state["Rows"]
        bar_y = int(self.state["top_row_index"] * self.height / len(Rows))
        bar_scroll_distance = int(self.height / len(Rows))

        # Offset the scrollbar according to transition progress.
        # Use the inverse of progress since offset decreases as it increases
        transition_progress = self.state["transition_progress"]

        if self.state["active_transition"] == "UP":
            return bar_y + int((1 - transition_progress) * bar_scroll_distance)

        if self.state["active_transition"] == "DOWN":
            return bar_y - int((1 - transition_progress) * bar_scroll_distance)

        return bar_y

    def _render_scrollbar(self, image):
        Rows = self.state["Rows"]
        horizontal_padding = self.state["scrollbar_horizontal_padding"]
        vertical_padding = self.state["scrollbar_vertical_padding"]
        bar_min_height = vertical_padding * 2
        bar_height = max(
            int(image.height * self.state["num_visible_rows"] / len(Rows)),
            bar_min_height,
        )
        bar_y = self._get_scrollbar_y()

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
        # bail if there are no rows to render
        num_rows = len(self.rows)
        if num_rows == 0:
            return image

        row_gap = self.state["row_gap"]
        row_height = self._get_row_height()
        rows_height = self._get_rows_height()

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
        active_transition = self.state["active_transition"]

        # when there is no transition render all rows without cropping
        if not active_transition:
            return self._render_rows(image)

        # when a transition is active there is one extra row, the row that is
        # being scrolled into view. Crop the rows according to scroll distance
        # and transition progress so the height of visible rows remains the same
        scroll_distance = self._get_row_height() + self.state["row_gap"]
        rows_height = self._get_rows_height()
        window_height = rows_height - scroll_distance

        progress = self.state["transition_progress"]
        progress_correction = (1 - progress) if active_transition == "UP" else progress

        window_top = int(scroll_distance * progress_correction)
        window_bottom = window_top + window_height

        if self.state["use_snapshot_when_scrolling"] and not self._rows_snapshot:
            self._rows_snapshot = self._render_rows(image)

        return (self._rows_snapshot or self._render_rows(image)).crop(
            (0, window_top, image.width, window_bottom)
        )

    def render(self, image):
        scrollbar_width = self.state["scrollbar_width"] if self.visible_scrollbar else 0
        border_width = (
            self.state["scrollbar_border_width"] if self.visible_scrollbar else 0
        )
        pages_width = (
            image.width
            if self.visible_scrollbar
            else image.width - scrollbar_width - border_width
        )

        # don't render scrollbar when all rows are visible
        if len(self.state["Rows"]) <= self.state["num_visible_rows"]:
            image.paste(self._render_rows(image))
            return image

        layers_arr = []
        if self.visible_scrollbar:
            layers_arr.append(
                layer(
                    self._render_scrollbar,
                    size=(scrollbar_width - border_width, image.height),
                )
            )
            layers_arr.append(
                layer(
                    rectangle,
                    size=(border_width, image.height),
                    pos=(scrollbar_width, 0),
                )
            )

        layers_arr.append(
            layer(
                self._render_rows_window,
                size=(pages_width, image.height),
                pos=(scrollbar_width + border_width, 0),
            ),
        )

        return apply_layers(image, layers_arr)
