import psutil
from pitop.common.formatting import bytes2human

from ...hotspots.base import HotspotInstance
from ...hotspots.progress_bar import Hotspot as ProgressBarHotspot
from ...hotspots.templates.marquee_dynamic_text import (
    Hotspot as MarqueeDynamicTextHotspot,
)
from ...hotspots.templates.text import Hotspot as TextHotspot
from ..base import Page as PageBase

X_MARGIN = 5
SUB_TITLE_WIDTH = 40
ROW_HEIGHT = 10
TITLE_FONT_SIZE = 12
TEXT_FONT_SIZE = 10
MARGIN_Y = 5
SPACING_Y = 2


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)
        self.reset()

    def reset(self):
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
        except Exception:
            memory = None
            swap = None

        def get_available_capacity(obj) -> str:
            try:
                return f"{bytes2human(obj.used)}/{bytes2human(obj.total)}"
            except Exception:
                return ""

        self.hotspot_instances = [
            HotspotInstance(
                TextHotspot(
                    size=(SUB_TITLE_WIDTH, ROW_HEIGHT),
                    font_size=TITLE_FONT_SIZE,
                    text="RAM",
                ),
                (X_MARGIN, MARGIN_Y),
            ),
            HotspotInstance(
                ProgressBarHotspot(
                    size=(self.size[0] - SUB_TITLE_WIDTH - X_MARGIN * 2, ROW_HEIGHT),
                    progress=lambda: memory.percent,
                ),
                (X_MARGIN + SUB_TITLE_WIDTH, MARGIN_Y),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.size[0] - X_MARGIN * 2, ROW_HEIGHT),
                    text=lambda: get_available_capacity(memory),
                    font_size=TEXT_FONT_SIZE,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT + SPACING_Y),
            ),
            HotspotInstance(
                TextHotspot(
                    size=(SUB_TITLE_WIDTH, ROW_HEIGHT),
                    font_size=TITLE_FONT_SIZE,
                    text="SWAP",
                ),
                (X_MARGIN, int(self.size[1] / 2) + MARGIN_Y),
            ),
            HotspotInstance(
                ProgressBarHotspot(
                    size=(self.size[0] - SUB_TITLE_WIDTH - X_MARGIN * 2, ROW_HEIGHT),
                    progress=lambda: swap.percent,
                ),
                (X_MARGIN + SUB_TITLE_WIDTH, int(self.size[1] / 2) + MARGIN_Y),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.size[0] - X_MARGIN * 2, ROW_HEIGHT),
                    text=lambda: get_available_capacity(swap),
                    font_size=TEXT_FONT_SIZE,
                ),
                (X_MARGIN, int(self.size[1] / 2) + MARGIN_Y + ROW_HEIGHT + SPACING_Y),
            ),
        ]
