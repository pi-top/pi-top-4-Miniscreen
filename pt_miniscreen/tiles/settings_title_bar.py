import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..hotspots.base import HotspotInstance
from ..hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ..hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from .base import Tile

logger = logging.getLogger(__name__)


class SettingsTitleBarTile(Tile):
    def __init__(self, size, pos) -> None:
        self.append_title = True
        self._text = "Settings"
        self.delimiter = " / "
        super().__init__(size, pos)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.reset()

    def reset(self):
        asst = MiniscreenAssistant("1", self.size)
        marquee_text_hotspot = MarqueeTextHotspot(
            size=self.size,
            text=self.text,
            font=asst.get_mono_font(
                size=14,
                bold=True,
            ),
            font_size=14,
        )
        marquee_text_xy = (
            # if no scroll is needed, center text in screen
            0
            if marquee_text_hotspot.needs_scrolling
            else int((self.size[0] - marquee_text_hotspot.text_image.width) / 2),
            0,
        )

        rect_hotspot = RectangleHotspot(
            size=(self.width, 1),
            bounding_box=(0, 0) + (self.width, 1),
        )
        rect_xy = (0, self.size[1] - 1)

        self.set_hotspot_instances(
            [
                HotspotInstance(marquee_text_hotspot, marquee_text_xy),
                HotspotInstance(rect_hotspot, rect_xy),
            ],
            start=True,
        )
