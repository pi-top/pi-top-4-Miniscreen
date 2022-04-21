import logging

from .list import List

logger = logging.getLogger(__name__)


class PageList(List):
    def __init__(
        self,
        Pages,
        num_visible_rows=None,  # take num_visible_rows out of kwargs
        row_gap=None,  # take row_gap out of kwargs
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            Rows=Pages,
            num_visible_rows=1,
            row_gap=0,
        )

    @property
    def current_page(self):
        return self.visible_rows[0]
