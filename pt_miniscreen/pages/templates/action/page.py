from typing import Dict

from ....hotspots.image_hotspot import Hotspot as ImageHotspot
from ....hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ....hotspots.status_icon_hotspot import Hotspot as StatusIconHotspot
from ....state import Speeds
from ....utils import get_image_file_path
from ...base import Page as PageBase
from .state import ActionState


class Page(PageBase):
    def __init__(
        self,
        interval,
        size,
        mode,
        config,
        get_state_method,
        set_state_method,
        icon,
        text,
    ):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.text = text
        self.icon = icon
        self.get_state_method = get_state_method
        self.set_state_method = set_state_method

        self.setup_hotspots()

    def setup_hotspots(self):
        SPACING = 4
        FONT_SIZE = 14
        STATUS_ICON_SIZE = 24
        ICON_WIDTH = 44
        ICON_HEIGHT = 33
        ICON_SIZE = (ICON_WIDTH, ICON_HEIGHT)

        FIRST_COLUMN_POS = 1
        FIRST_COLUMN_WIDTH = ICON_WIDTH + FIRST_COLUMN_POS

        THIRD_COLUMN_WIDTH = STATUS_ICON_SIZE
        THIRD_COLUMN_POS = self.width - THIRD_COLUMN_WIDTH - SPACING

        SECOND_COLUMN_POS = FIRST_COLUMN_WIDTH + SPACING
        SECOND_COLUMN_WIDTH = THIRD_COLUMN_POS - SECOND_COLUMN_POS - SPACING

        self.status_icon_hotspot = StatusIconHotspot(
            interval=Speeds.ACTION_STATE_UPDATE.value,
            mode=self.mode,
            size=(THIRD_COLUMN_WIDTH, STATUS_ICON_SIZE),
        )

        self.action_state = ActionState.ENABLED

        if callable(self.get_state_method):
            if self.get_state_method() != "Enabled":
                self.action_state = ActionState.DISABLED

        self.hotspots: Dict = {
            (FIRST_COLUMN_POS, self.vertical_middle_position(ICON_HEIGHT)): [
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=ICON_SIZE,
                    image_path=get_image_file_path(f"settings/{self.icon}.png"),
                ),
            ],
            (SECOND_COLUMN_POS, self.vertical_middle_position(FONT_SIZE)): [
                MarqueeTextHotspot(
                    interval=Speeds.MARQUEE.value,
                    mode=self.mode,
                    size=(SECOND_COLUMN_WIDTH, FONT_SIZE),
                    text=self.text,
                    font_size=FONT_SIZE,
                )
            ],
            (THIRD_COLUMN_POS, self.vertical_middle_position(STATUS_ICON_SIZE)): [
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
