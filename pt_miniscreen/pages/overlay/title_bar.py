import logging
from typing import Dict

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ..base import Page as PageBase

logger = logging.getLogger(__name__)


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval, size, mode, config)

        asst = MiniscreenAssistant(mode, size)

        self.hotspots: Dict = {
            (0, 0): [
                TextHotspot(
                    interval=interval,
                    mode=mode,
                    size=size,
                    text="Title Bar",
                    font=asst.get_mono_font_path(bold=True),
                    font_size=14,
                    fill="white",
                )
            ],
            (0, size[1] - 1): [
                RectangleHotspot(
                    interval=interval,
                    mode=mode,
                    size=(size[0], 1),
                    bounding_box=(0, 0) + (size[0], 1),
                )
            ],
        }
