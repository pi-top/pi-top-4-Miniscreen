import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..event import AppEvents, subscribe
from ..hotspots.base import HotspotInstance
from ..hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ..hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from .base import Tile

logger = logging.getLogger(__name__)


class SettingsTitleBarTile(Tile):
    def __init__(self, size, pos, text="Settings", append_title=True) -> None:
        super().__init__(size, pos)
        self.append_title = append_title
        self._text = text

        def handle_go_to_child(menu_name):
            if not self.append_title:
                return

            self._text = f"{self._text} / {text}"

        def handle_go_to_parent():
            if not self.append_title:
                return

            menu_id_fields = self._text.split(".")

            if len(menu_id_fields) == 1:
                return

            self._text = ".".join(menu_id_fields[:-1])

        subscribe(AppEvents.GO_TO_CHILD_MENU, handle_go_to_child)
        subscribe(AppEvents.GO_TO_PARENT_MENU, handle_go_to_parent)

    def reset(self):
        asst = MiniscreenAssistant("1", self.size)
        marquee_text_hotspot = MarqueeTextHotspot(
            size=self.size,
            text=self._text,
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

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        if size == self.size:
            return

        self.size = size
        self.reset()
