from enum import Enum, auto

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..base import PageBase as _PageBase


class TextPage(_PageBase):
    def __init__(self, text, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.text = text

    def render(self, image):
        MiniscreenAssistant(self.mode, self.size).render_text(
            image,
            text=self.text,
            wrap=self.wrap,
            font_size=self.font_size,
        )


class Page(Enum):
    BATTERY = auto()
