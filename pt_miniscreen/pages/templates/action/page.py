from typing import Dict

from ....hotspots.image_hotspot import Hotspot as ImageHotspot
from ....hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ....hotspots.status_icon_hotspot import Hotspot as StatusIconHotspot
from ....utils import get_image_file_path
from ...base import Page as PageBase
from .state import ActionState


class Page(PageBase):
    def __init__(
        self,
        size,
        get_state_method,
        set_state_method,
        icon,
        text,
    ):
        self.text = text
        self.icon = icon
        self.get_state_method = get_state_method
        self.set_state_method = set_state_method

        super().__init__(size=size)

    def reset(self):
        SPACING = 4
        FONT_SIZE = 14
        STATUS_ICON_SIZE = 24
        ICON_WIDTH = 44

        FIRST_COLUMN_POS = 1
        FIRST_COLUMN_WIDTH = ICON_WIDTH + FIRST_COLUMN_POS

        THIRD_COLUMN_WIDTH = STATUS_ICON_SIZE
        THIRD_COLUMN_POS = self.width - THIRD_COLUMN_WIDTH - SPACING

        SECOND_COLUMN_POS = FIRST_COLUMN_WIDTH + SPACING
        SECOND_COLUMN_WIDTH = THIRD_COLUMN_POS - SECOND_COLUMN_POS - SPACING

        self.status_icon_hotspot = StatusIconHotspot(
            size=(THIRD_COLUMN_WIDTH, STATUS_ICON_SIZE),
        )

        self.action_state = ActionState.ENABLED

        if callable(self.get_state_method):
            if self.get_state_method() != "Enabled":
                self.action_state = ActionState.DISABLED

        self.hotspots: Dict = {
            (FIRST_COLUMN_POS, 0): [
                ImageHotspot(
                    size=(ICON_WIDTH, self.height),
                    image_path=get_image_file_path(f"settings/{self.icon}.png"),
                ),
            ],
            (SECOND_COLUMN_POS, (self.height - FONT_SIZE) / 2): [
                MarqueeTextHotspot(
                    size=(SECOND_COLUMN_WIDTH, FONT_SIZE),
                    text=self.text,
                    font_size=FONT_SIZE,
                )
            ],
            (THIRD_COLUMN_POS, (self.height - STATUS_ICON_SIZE) / 2): [
                self.status_icon_hotspot
            ],
        }

    @property
    def action_state(self):
        return self.status_icon_hotspot.action_state

    @action_state.setter
    def action_state(self, state: ActionState):
        if state == ActionState.UNKNOWN:
            # If unknown state is entered into after initialisation
            # stay in that state until page is reset
            return

        if state == ActionState.PROCESSING:
            # Update state of processing hotspot
            pass

        self.status_icon_hotspot.action_state = state

    def reset(self):
        self.action_state = ActionState.ENABLED

        if callable(self.get_state_method):
            if self.get_state_method() != "Enabled":
                self.action_state = ActionState.DISABLED

        # TODO: reset hotspots?
        # processing_icon_frame = 0

    def on_select_press(self):
        if self.action_state == ActionState.PROCESSING:
            return

        if not callable(self.set_state_method):
            return

        self.action_state = ActionState.PROCESSING
        self.set_state_method()
        self.action_state = ActionState.UNKNOWN
        self.reset()
