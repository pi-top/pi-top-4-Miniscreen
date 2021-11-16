import logging
from typing import Dict

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...event import AppEvents, post_event
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ...state import Speeds
from ...viewport import HotspotManager

logger = logging.getLogger(__name__)


class TitleBar(HotspotManager):
    def __init__(
        self, viewport_size, window_size, window_position, title_bar_behaviour
    ) -> None:
        super().__init__(viewport_size, window_size, window_position)
        self.mode = "1"
        self._behaviour = title_bar_behaviour

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
    def behaviour(self, title_bar_behaviour):
        if self.behaviour == title_bar_behaviour or title_bar_behaviour is None:
            return

        if title_bar_behaviour.append_title:
            self.behaviour.text = f"{self.behaviour.text} / {title_bar_behaviour.text}"
        else:
            self.behaviour.text = title_bar_behaviour.text

        self.behaviour.visible = title_bar_behaviour.visible
        if title_bar_behaviour.height is not None:
            self.behaviour.height = title_bar_behaviour.height

        height = self.behaviour.height
        if not title_bar_behaviour.visible or title_bar_behaviour.text == "":
            height = 0
        elif title_bar_behaviour.height:
            height = title_bar_behaviour.height

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
                    (self.window_size[0] - marquee_text_hotspot.text_image.width) / 2
                )

            self.hotspots: Dict = {
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
