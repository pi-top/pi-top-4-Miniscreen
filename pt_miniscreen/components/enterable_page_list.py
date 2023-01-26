import logging

from pt_miniscreen.components.mixins import (
    Actionable,
    Enterable,
    Navigable,
    HasGutterIcons,
)
from pt_miniscreen.core.components.page_list import PageList
from pt_miniscreen.utils import get_image_file_path


logger = logging.getLogger(__name__)


class EnterablePageList(PageList, Navigable, Enterable, HasGutterIcons):
    def __init__(
        self,
        Pages,
        num_visible_rows=None,  # take num_visible_rows out of kwargs
        row_gap=None,  # take row_gap out of kwargs
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            Pages=Pages,
            num_visible_rows=1,
            row_gap=0,
        )

    @property
    def enterable_component(self):
        if isinstance(self.current_page, Enterable):
            return self.current_page.enterable_component
        return None

    def top_gutter_icon(self):
        if self.can_scroll_up():
            return get_image_file_path("gutter/top_arrow.png")

    def bottom_gutter_icon(self):
        if isinstance(self.current_page, Actionable):
            return get_image_file_path("gutter/tick.png")

        if isinstance(self.current_page, Enterable):
            return get_image_file_path("gutter/right_arrow.png")

    def go_next(self):
        return super().scroll_down()

    def go_previous(self):
        return super().scroll_up()

    def go_top(self):
        return super().scroll_to_top()
