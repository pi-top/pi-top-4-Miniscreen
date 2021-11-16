import logging
from typing import Dict

from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from pt_miniscreen.state import Speeds

from ...event import AppEvents, post_event
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ..base import Page as PageBase

logger = logging.getLogger(__name__)


class Page(PageBase):
    def __init__(self, interval, size, mode, config, title_bar_behaviour):
        super().__init__(interval, size, mode, config)
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

        self.height = self.behaviour.height
        if not title_bar_behaviour.visible or title_bar_behaviour.text == "":
            self.height = 0
        elif title_bar_behaviour.height:
            self.height = title_bar_behaviour.height

        post_event(AppEvents.TITLE_BAR_HEIGHT_SET, self.height)

        if self.height != 0:
            asst = MiniscreenAssistant(self.mode, self.size)
            marquee_text_hotspot = MarqueeTextHotspot(
                interval=Speeds.MARQUEE.value,
                mode=self.mode,
                size=self.size,
                text=self.behaviour.text,
                font=asst.get_mono_font(
                    size=self.font_size,
                    bold=True,
                ),
                font_size=14,
            )
            marquee_hotspot_x_pos = 0
            if not marquee_text_hotspot.needs_scrolling:
                # if no scroll is needed, center text in screen
                marquee_hotspot_x_pos = int(
                    (self.width - marquee_text_hotspot.text_image.width) / 2
                )

            self.hotspots: Dict = {
                (marquee_hotspot_x_pos, 0): [marquee_text_hotspot],
                (0, self.height - 1): [
                    RectangleHotspot(
                        interval=self.interval,
                        mode=self.mode,
                        size=(self.width, 1),
                        bounding_box=(0, 0) + (self.width, 1),
                    )
                ],
            }
