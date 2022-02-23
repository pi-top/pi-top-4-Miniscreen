import logging
from typing import Callable, Optional

from ....event import AppEvent, subscribe
from ....hotspots.base import HotspotInstance
from ....hotspots.templates.status_icon import Hotspot as StatusIconHotspot
from ....hotspots.templates.text import Hotspot as TextHotspot
from ....types import Coordinate
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
        font_size=14,
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

        super().__init__(size=size, font_size=font_size)
        self.reset()

    def reset(self) -> None:
        SPACING = 8
        FIRST_COLUMN_POS = SPACING
        FIRST_COLUMN_WIDTH = 52
        SECOND_COLUMN_POS = FIRST_COLUMN_POS + FIRST_COLUMN_WIDTH + SPACING

        if not callable(self.get_state_method):
            self.action_state = ActionState.IDLE
        elif self.get_state_method() != "Enabled":
            self.action_state = ActionState.DISABLED
        else:
            self.action_state = ActionState.ENABLED

        self.hotspot_instances = [
            HotspotInstance(
                TextHotspot(
                    size=(FIRST_COLUMN_WIDTH, self.size[1]),
                    text=self.text,
                    font_size=self.font_size,
                    align="right",
                    vertical_align="center",
                ),
                (FIRST_COLUMN_POS, 0),
            ),
            HotspotInstance(
                self.status_icon_hotspot,
                (
                    SECOND_COLUMN_POS,
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
            self.action_state = ActionState.UNKNOWN
            logger.error(f"Failed to start action: {e}")
