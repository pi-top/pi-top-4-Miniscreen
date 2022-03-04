import logging

from pt_miniscreen.utils import get_mono_font

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.marquee_text import Hotspot as MarqueeTextHotspot
from ...hotspots.templates.rectangle import Hotspot as RectangleHotspot
from ..base import Tile

logger = logging.getLogger(__name__)


class SettingsTitleBarTile(Tile):
    def __init__(self, size, pos) -> None:
        self.append_title = True
        self._text = "Settings"
        self.delimiter = " / "
        super().__init__(size, pos)
        self.reset()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self.reset()

    def reset(self) -> None:
        margin = 2
        marquee_text_hotspot = MarqueeTextHotspot(
            size=(self.size[0] - 2 * margin, self.size[1]),
            text=self.text,
            font=get_mono_font(
                size=14,
                bold=True,
            ),
            font_size=14,
        )
        marquee_text_xy = (
            margin if marquee_text_hotspot.needs_scrolling
            # if no scroll is needed, center text in screen
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
            ]
        )
