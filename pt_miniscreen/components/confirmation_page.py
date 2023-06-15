from functools import partial
from typing import Callable, Optional
from weakref import ref

from pt_miniscreen.components.mixins import (
    Actionable,
    HasGutterIcons,
    Navigable,
    Poppable,
    UpdatableByChild,
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
PADDING = 5


class ConfirmationPage(Component, Actionable, Navigable):
    def __init__(
        self,
        parent: UpdatableByChild,
        title: Optional[str] = None,
        font_size: Optional[int] = None,
        options_font_size: Optional[int] = None,
        confirm_text: Optional[str] = None,
        cancel_text: Optional[str] = None,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        title_max_height: Optional[int] = None,
        **kwargs,
    ) -> None:
        if title is None:
            title = "Are you sure?"
        if confirm_text is None:
            confirm_text = "Yes"
        if cancel_text is None:
            cancel_text = "No"
        if font_size is None:
            font_size = TITLE_FONT_SIZE
        if options_font_size is None:
            options_font_size = OPTIONS_FONT_SIZE
        if title_max_height is None:
            title_max_height = font_size

        self.parent_ref = ref(parent)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.font_size = font_size
        self.options_font_size = options_font_size
        self.title_max_height = title_max_height

        self.title = Text(
            text=title,
            font_size=font_size,
            **kwargs,
        )
        self.selectable_list = SelectableList(
            Rows=[
                partial(
                    MarqueeText, text=self.confirm_text, font_size=options_font_size
                ),
                partial(
                    MarqueeText, text=self.cancel_text, font_size=options_font_size
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
        if self.selectable_list.selected_row.text == self.confirm_text:
            if callable(self.on_confirm):
                self.on_confirm()
        elif self.selectable_list.selected_row.text == self.cancel_text:
            if callable(self.on_cancel):
                self.on_cancel()
        else:
            return

        if isinstance(self.parent_ref(), UpdatableByChild):
            self.parent_ref().on_child_action()

    def render(self, image):
        SEPARATOR_HEIGHT = 1
        return apply_layers(
            image,
            [
                layer(
                    self.title.render,
                    size=(image.width, self.title_max_height),
                    pos=(0, 0),
                ),
                layer(
                    rectangle,
                    size=(image.width, SEPARATOR_HEIGHT),
                    pos=(0, self.title_max_height + 1),
                ),
                layer(
                    self.selectable_list.render,
                    size=(
                        image.width,
                        2 * self.options_font_size + PADDING,
                    ),
                    pos=(0, self.title_max_height + 2 + SEPARATOR_HEIGHT * 2),
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


class AppConfirmationPage(ConfirmationPage, HasGutterIcons, Poppable):
    def __init__(
        self,
        on_confirm_pop_elements: Optional[int] = None,
        on_cancel_pop_elements: Optional[int] = None,
        **kwargs,
    ) -> None:
        if on_confirm_pop_elements is None:
            on_confirm_pop_elements = 1
        if on_cancel_pop_elements is None:
            on_cancel_pop_elements = 1

        self.on_confirm_pop_elements = on_confirm_pop_elements
        self.on_cancel_pop_elements = on_cancel_pop_elements

        super().__init__(**kwargs)

    def perform_action(self):
        super().perform_action()

        if self.selectable_list.selected_row.text == self.confirm_text:
            elements = self.on_confirm_pop_elements
        elif self.selectable_list.selected_row.text == self.cancel_text:
            elements = self.on_cancel_pop_elements
        else:
            return

        self.pop(elements)

    def top_gutter_icon(self):
        return get_image_file_path("gutter/left_arrow.png")

    def bottom_gutter_icon(self):
        return get_image_file_path("gutter/tick.png")
