import logging

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...event import AppEvents, subscribe
from ...hotspots.base import HotspotInstance
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ...tiles import Tile

logger = logging.getLogger(__name__)


class TitleBar(Tile):
    def __init__(self, size, behaviour) -> None:
        super().__init__(size)
        self.mode = "1"
        self._behaviour = behaviour
        self.active = True

        def handle_go_to_child(menu_name):
            if not self.behaviour.append_title:
                return

            self.behaviour.text = f"{self.behaviour.text} / {behaviour.text}"

        def handle_go_to_parent():
            if not self.behaviour.append_title:
                return

            menu_id_fields = self.behaviour.text.split(".")

            if len(menu_id_fields) == 1:
                return

            self.behaviour.text = ".".join(menu_id_fields[:-1])

        subscribe(AppEvents.GO_TO_CHILD_MENU, handle_go_to_child)
        subscribe(AppEvents.GO_TO_PARENT_MENU, handle_go_to_parent)

    def setup_hotspots(self):
        asst = MiniscreenAssistant(self.mode, self.size)
        marquee_text_hotspot = MarqueeTextHotspot(
            mode=self.mode,
            size=self.size,
            text=self.behaviour.text,
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
            mode=self.mode,
            size=(self.width, 1),
            bounding_box=(0, 0) + (self.width, 1),
        )
        rect_xy = (0, self.height - 1)

        hotspots = [
            HotspotInstance(marquee_text_hotspot, marquee_text_xy),
            HotspotInstance(rect_hotspot, rect_xy),
        ]

        self.reset_with_hotspot_instances(hotspots)

    @property
    def height(self):
        return self.behaviour.height

    @height.setter
    def height(self, new_height):
        self.behaviour.height = new_height

    @property
    def behaviour(self):
        return self._behaviour

    @behaviour.setter
    def behaviour(self, behaviour):
        if self.behaviour == behaviour or behaviour is None:
            return

        self.setup_hotspots()
