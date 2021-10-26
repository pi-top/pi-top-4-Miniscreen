import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .base import HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(
        self, interval, size, mode, text, font_size=20, xy=None, anchor=None, align=None
    ):
        super().__init__(interval, size, mode)

        self.assistant = MiniscreenAssistant(self.mode, self.size)
        self._text = text
        self.font_size = font_size
        if xy is None:
            xy = (0, 0)
        self.xy = xy
        self.anchor = anchor
        self.align = align

    def render(self, image):
        self.assistant.render_text(
            image,
            text=self.text,
            xy=self.xy,
            font_size=self.font_size,
            anchor=self.anchor,
            align=self.align,
        )

    @property
    def text(self):
        if callable(self._text):
            return self._text()
        return self._text

    @text.setter
    def text(self, value_or_callback):
        self._text = value_or_callback
