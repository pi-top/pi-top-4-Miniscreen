import logging
from typing import Dict

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...event import AppEvents, post_event
from ...hotspots.base import HotspotInstance
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ...state import Speeds
from ...tiles import Tile

logger = logging.getLogger(__name__)


class TitleBar(Tile):
    def __init__(self, tile_size, behaviour) -> None:
        super().__init__(tile_size)
        self.mode = "1"
        self._behaviour = behaviour

    def should_draw(self):
        return (
            self.behaviour.height != 0
            and self.behaviour.text != ""
            and self.behaviour.visible is True
        )

    @property
    def behaviour(self):
        return self._behaviour

    @behaviour.setter
    def behaviour(self, behaviour):
        if self.behaviour == behaviour or behaviour is None:
            return

        if behaviour.append_title:
            self.behaviour.text = f"{self.behaviour.text} / {behaviour.text}"
        else:
            self.behaviour.text = behaviour.text

        self.behaviour.visible = behaviour.visible
        if behaviour.height is not None:
            self.behaviour.height = behaviour.height

        height = self.behaviour.height
        if not behaviour.visible or behaviour.text == "":
            height = 0
        elif behaviour.height:
            height = behaviour.height

        post_event(AppEvents.TITLE_BAR_HEIGHT_SET, height)

        if height != 0:
            asst = MiniscreenAssistant(self.mode, self.viewport_size)
            marquee_text_hotspot = MarqueeTextHotspot(
                interval=Speeds.MARQUEE.value,
                mode=self.mode,
                size=self.viewport_size,
                text=self.behaviour.text,
                font=asst.get_mono_font(
                    size=14,
                    bold=True,
                ),
                font_size=14,
            )
            marquee_hotspot_x_pos = 0
            if not marquee_text_hotspot.needs_scrolling:
                # if no scroll is needed, center text in screen
                marquee_hotspot_x_pos = int(
                    (self.tile_size[0] - marquee_text_hotspot.text_image.width) / 2
                )

            hotspots: Dict = {
                (marquee_hotspot_x_pos, 0): [marquee_text_hotspot],
                (0, height - 1): [
                    RectangleHotspot(
                        interval=Speeds.DYNAMIC_PAGE_REDRAW.value,
                        mode=self.mode,
                        size=(self.viewport_size[0], 1),
                        bounding_box=(0, 0) + (self.viewport_size[0], 1),
                    )
                ],
            }

            self.remove_all_hotspots()
            self.stop_threads()
            for xy, hotspots in hotspots.items():
                for hotspot in hotspots:
                    self.register(HotspotInstance(hotspot, xy))
