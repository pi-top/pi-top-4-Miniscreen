import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..state import Speeds
from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(
        self,
        size,
        text,
        font_size=20,
        xy=None,
        font=None,
        fill=1,
        anchor=None,
        align=None,
        interval=Speeds.DYNAMIC_PAGE_REDRAW.value,
    ):
        super().__init__(interval=interval, size=size)

        self.assistant = MiniscreenAssistant("1", self.size)
        self._text = text
        self.font_size = font_size

        if xy is None:
            xy = (int(size[0] / 2), int(size[1] / 2))
        self.xy = xy
        self.anchor = anchor
        self.align = align

        self.font = font
        self.fill = fill

    def render(self, image):
        self.assistant.render_text(
            image,
            text=self.text,
            xy=self.xy,
            font_size=self.font_size,
            font=self.font,
            fill=self.fill,
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
