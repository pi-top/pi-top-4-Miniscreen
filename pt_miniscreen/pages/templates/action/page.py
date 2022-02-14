import logging
from typing import Callable, Optional

from ....event import AppEvent, subscribe
from ....hotspots.base import HotspotInstance
from ....hotspots.templates.image import Hotspot as ImageHotspot
from ....hotspots.templates.marquee_text import Hotspot as MarqueeTextHotspot
from ....hotspots.templates.status_icon import Hotspot as StatusIconHotspot
from ....types import Coordinate
from ....utils import get_image_file_path
from ...base import Page as PageBase
from .state import ActionState

logger = logging.getLogger(__name__)


class Page(PageBase):
    STATUS_ICON_SIZE = 24
    THIRD_COLUMN_WIDTH = STATUS_ICON_SIZE

    def __init__(
        self,
        size: Coordinate,
        get_state_method: Optional[Callable],
        set_state_method: Callable,
        icon: str,
        text: str,
    ) -> None:
        self.text = text
        self.icon = icon
        self.get_state_method = get_state_method
        self.set_state_method = set_state_method
        self.status_icon_hotspot = StatusIconHotspot(
            size=(self.THIRD_COLUMN_WIDTH, self.STATUS_ICON_SIZE),
        )

        def reset_if_processing():
            if self.action_state == ActionState.PROCESSING:
                self.reset()

        subscribe(AppEvent.ACTION_TIMEOUT, reset_if_processing)
        subscribe(AppEvent.ACTION_FINISH, reset_if_processing)

        super().__init__(size=size)
        self.reset()

    def reset(self) -> None:
        SPACING = 4
        FONT_SIZE = 14
        ICON_WIDTH = 44
        ICON_HEIGHT = 33
        ICON_SIZE = (ICON_WIDTH, ICON_HEIGHT)

        FIRST_COLUMN_POS = 1
        FIRST_COLUMN_WIDTH = ICON_WIDTH + FIRST_COLUMN_POS

        THIRD_COLUMN_POS = self.width - self.THIRD_COLUMN_WIDTH - SPACING

        SECOND_COLUMN_POS = FIRST_COLUMN_WIDTH + SPACING
        SECOND_COLUMN_WIDTH = THIRD_COLUMN_POS - SECOND_COLUMN_POS - SPACING

        if not callable(self.get_state_method):
            self.action_state = ActionState.IDLE
        elif self.get_state_method() != "Enabled":
            self.action_state = ActionState.DISABLED
        else:
            self.action_state = ActionState.ENABLED

        self.hotspot_instances = [
            HotspotInstance(
                ImageHotspot(
                    size=ICON_SIZE,
                    image_path=get_image_file_path(f"settings/{self.icon}.png"),
                ),
                (FIRST_COLUMN_POS, self.offset_pos_for_vertical_center(ICON_HEIGHT)),
            ),
            HotspotInstance(
                MarqueeTextHotspot(
                    size=(SECOND_COLUMN_WIDTH, FONT_SIZE),
                    text=self.text,
                    font_size=FONT_SIZE,
                ),
                (SECOND_COLUMN_POS, self.offset_pos_for_vertical_center(FONT_SIZE)),
            ),
            HotspotInstance(
                self.status_icon_hotspot,
                (
                    THIRD_COLUMN_POS,
                    self.offset_pos_for_vertical_center(self.STATUS_ICON_SIZE),
                ),
            ),
        ]

    @property
    def action_state(self) -> ActionState:
        return self.status_icon_hotspot.action_state

    @action_state.setter
    def action_state(self, state: ActionState) -> None:
        if state == self.status_icon_hotspot.action_state:
            return

        if state == ActionState.UNKNOWN:
            # If unknown state is entered into after initialisation
            # stay in that state until page is reset
            return

        self.status_icon_hotspot.action_state = state

    def start_action(self) -> None:
        if self.action_state == ActionState.PROCESSING:
            return

        if not callable(self.set_state_method):
            return

        self.action_state = ActionState.PROCESSING

        try:
            self.set_state_method()
        except Exception as e:
            logger.error(e)
