import logging

from .list import List

logger = logging.getLogger(__name__)


class PageList(List):
    smoothness = 0.5

    def __init__(
        self,
        Pages,
        **kwargs,
    ):
        assert len(Pages) > 0

        super().__init__(
            **kwargs,
            Rows=Pages,
            num_visible_rows=1,
            row_gap=0,
        )

    @property
    def current_page(self):
        return self.visible_rows[0]
