import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .base import HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode, text, font_size=20, xy=None):
        super().__init__(interval, size, mode)

        self.assistant = MiniscreenAssistant(self.mode, self.size)
        self._text = text
        self.font_size = font_size
        if xy is None:
            xy = (0, 0)
        self.xy = xy

    def render(self, image):
        self.assistant.render_text(
            image,
            text=self.text,
            xy=self.xy,
            font_size=self.font_size,
            # anchor="la",
            # align="left"
        )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
