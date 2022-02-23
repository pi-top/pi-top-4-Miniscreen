import logging
from typing import Callable, Union

import PIL.ImageDraw

from ..state import Speeds
from ..types import Coordinate
from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(
        self,
        size: Coordinate,
        progress: Union[Callable, float],
        interval: float = Speeds.DYNAMIC_PAGE_REDRAW.value,
    ):
        self.progress = progress
        super().__init__(interval=interval / 2, size=size)

    def render(self, image):
        margin = 1
        draw = PIL.ImageDraw.Draw(image)

        try:
            percent = self.progress() if callable(self.progress) else self.progress
        except Exception as e:
            logger.error(f"progress_bar error: {e}.")
            percent = 0.0

        draw.rectangle(
            (0, 0) + (self.size[0] - margin, self.size[1] - margin), "black", "white"
        )
        draw.rectangle(
            (0, 0) + (self.size[0] * percent / 100.0, self.size[1] - margin),
            "white",
            "white",
        )
