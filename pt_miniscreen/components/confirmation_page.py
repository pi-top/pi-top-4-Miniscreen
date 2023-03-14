from functools import partial
from typing import Callable, Optional

from pt_miniscreen.components.mixins import (
    Actionable,
    HasGutterIcons,
    Navigable,
    Poppable,
)
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.core.utils import apply_layers, layer, rectangle
from pt_miniscreen.utils import get_image_file_path

import logging

logger = logging.getLogger(__name__)


TITLE_FONT_SIZE = 14
OPTIONS_FONT_SIZE = 13
SELECTABLE_LIST_VERTICAL_OFFSET = 5


class ConfirmationPage(Component, Actionable, HasGutterIcons, Poppable, Navigable):
    def __init__(
        self,
        title: Optional[str],
        confirm_text: Optional[str],
        cancel_text: Optional[str],
        on_confirm: Callable,
        on_cancel: Optional[Callable],
        **kwargs,
    ) -> None:

        if title is None:
            title = "Are you sure?"
        if confirm_text is None:
            confirm_text = "Yes"
        if cancel_text is None:
            cancel_text = "No"

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

        self.title = Text(
            text=title,
            font_size=TITLE_FONT_SIZE,
            **kwargs,
        )
        self.selectable_list = SelectableList(
            Rows=[
                partial(
                    MarqueeText, text=self.confirm_text, font_size=OPTIONS_FONT_SIZE
                ),
                partial(
                    MarqueeText, text=self.cancel_text, font_size=OPTIONS_FONT_SIZE
                ),
            ],
            num_visible_rows=2,
            **kwargs,
        )

        super().__init__(
            **kwargs, initial_state={"selected_row": self.selectable_list.selected_row}
        )

    def perform_action(self):
        logging.info(
            f"ConfirmationPage.perform_action: user selected '{self.selectable_list.selected_row.text}', executing callback"
        )

        elements_to_pop = 1
        if self.selectable_list.selected_row.text == self.confirm_text and callable(
            self.on_confirm
        ):
            self.on_confirm()
            elements_to_pop = 2
        elif self.selectable_list.selected_row.text == self.cancel_text and callable(
            self.on_cancel
        ):
            self.on_cancel()

        self.pop(elements=elements_to_pop)

    def top_gutter_icon(self):
        return get_image_file_path("gutter/left_arrow.png")

    def bottom_gutter_icon(self):
        return get_image_file_path("gutter/tick.png")

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.title.render, size=(image.width, TITLE_FONT_SIZE), pos=(0, 0)
                ),
                layer(rectangle, size=(image.width, 1), pos=(0, TITLE_FONT_SIZE)),
                layer(
                    self.selectable_list.render,
                    size=(
                        image.width,
                        OPTIONS_FONT_SIZE * 2 + SELECTABLE_LIST_VERTICAL_OFFSET,
                    ),
                    pos=(0, TITLE_FONT_SIZE + SELECTABLE_LIST_VERTICAL_OFFSET),
                ),
            ],
        )

    def go_next(self):
        self.selectable_list.select_next_row()
        self.state.update({"selected_row": self.selectable_list.selected_row})

    def go_previous(self):
        self.selectable_list.select_previous_row()
        self.state.update({"selected_row": self.selectable_list.selected_row})

    def go_top(self):
        pass
