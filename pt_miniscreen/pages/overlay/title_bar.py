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
        self.current_behaviour = title_bar_behaviour
        self.update(title_bar_behaviour)

    def should_draw(self):
        return (
            self.current_behaviour.height != 0
            and self.current_behaviour.text != ""
            and self.current_behaviour.visible is True
        )

    def update(self, title_bar_behaviour):
        if self.current_behaviour == title_bar_behaviour or title_bar_behaviour is None:
            return

        if title_bar_behaviour.append_title:
            self.current_behaviour.text = (
                f"{self.current_behaviour.text} / {title_bar_behaviour.text}"
            )
        else:
            self.current_behaviour.text = title_bar_behaviour.text
        self.current_behaviour.visible = title_bar_behaviour.visible
        if title_bar_behaviour.height is not None:
            self.current_behaviour.height = title_bar_behaviour.height

        if title_bar_behaviour.visible is False or title_bar_behaviour.text == "":
            self.height = 0
        else:
            self.height = (
                title_bar_behaviour.height
                if title_bar_behaviour.height
                else self.current_behaviour.height
            )

        post_event(AppEvents.TITLE_BAR_HEIGHT_CHANGED, self.height)

        if self.height != 0:
            asst = MiniscreenAssistant(self.mode, self.size)
            self.hotspots: Dict = {
                (0, 0): [
                    MarqueeTextHotspot(
                        interval=Speeds.MARQUEE.value,
                        mode=self.mode,
                        size=self.size,
                        text=self.current_behaviour.text,
                        font=asst.get_mono_font(
                            size=self.font_size
                        ),  # bold=True, TODO: provide support in SDK
                        font_size=14,
                    )
                ],
                (0, self.height - 1): [
                    RectangleHotspot(
                        interval=self.interval,
                        mode=self.mode,
                        size=(self.width, 1),
                        bounding_box=(0, 0) + (self.width, 1),
                    )
                ],
            }
