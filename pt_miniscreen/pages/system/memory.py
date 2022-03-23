from typing import Callable

import psutil
from pitop.common.formatting import bytes2human

from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.hotspots.marquee_text import MarqueeText
from pt_miniscreen.core.hotspots.text import Text
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.progress_bar import ProgressBar

X_MARGIN = 4
SUB_TITLE_WIDTH = 40
ROW_HEIGHT = 10
TITLE_FONT_SIZE = 12
TEXT_FONT_SIZE = 10
MARGIN_Y = 5
SPACING_Y = 3


class MemoryPage(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def get_usage_string(func: Callable) -> str:
            try:
                memory_object = func()
                return f"{bytes2human(memory_object.used)}/{bytes2human(memory_object.total)}"
            except Exception:
                return ""

        def get_usage_percentage(func: Callable) -> float:
            try:
                return func().percent
            except Exception:
                return 0.0

        self.ram_title = self.create_hotspot(
            Text, text="RAM", font_size=TITLE_FONT_SIZE
        )
        self.ram_progress_bar = self.create_hotspot(
            ProgressBar,
            progress=lambda: get_usage_percentage(func=psutil.virtual_memory),
        )
        self.ram_text = self.create_hotspot(
            MarqueeText,
            font_size=TEXT_FONT_SIZE,
            get_text=lambda: get_usage_string(func=psutil.virtual_memory),
        )

        self.swap_title = self.create_hotspot(
            Text, text="SWAP", font_size=TITLE_FONT_SIZE
        )
        self.swap_progress_bar = self.create_hotspot(
            ProgressBar, progress=lambda: get_usage_percentage(func=psutil.swap_memory)
        )
        self.swap_text = self.create_hotspot(
            MarqueeText,
            font_size=TEXT_FONT_SIZE,
            get_text=lambda: get_usage_string(func=psutil.swap_memory),
        )

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.ram_title.render,
                    size=(SUB_TITLE_WIDTH, ROW_HEIGHT),
                    pos=(X_MARGIN, MARGIN_Y),
                ),
                layer(
                    self.ram_progress_bar.render,
                    size=(image.width - SUB_TITLE_WIDTH - X_MARGIN * 2, ROW_HEIGHT),
                    pos=(X_MARGIN + SUB_TITLE_WIDTH, MARGIN_Y),
                ),
                layer(
                    self.ram_text.render,
                    size=(image.width - X_MARGIN * 2, ROW_HEIGHT),
                    pos=(X_MARGIN, MARGIN_Y + ROW_HEIGHT + SPACING_Y),
                ),
                layer(
                    self.swap_title.render,
                    size=(SUB_TITLE_WIDTH, ROW_HEIGHT),
                    pos=(X_MARGIN, int(image.height / 2) + MARGIN_Y),
                ),
                layer(
                    self.swap_progress_bar.render,
                    size=(image.width - SUB_TITLE_WIDTH - X_MARGIN * 2, ROW_HEIGHT),
                    pos=(X_MARGIN + SUB_TITLE_WIDTH, int(image.height / 2) + MARGIN_Y),
                ),
                layer(
                    self.swap_text.render,
                    size=(image.width - X_MARGIN * 2, ROW_HEIGHT),
                    pos=(
                        X_MARGIN,
                        int(image.height / 2) + MARGIN_Y + ROW_HEIGHT + SPACING_Y,
                    ),
                ),
            ],
        )
