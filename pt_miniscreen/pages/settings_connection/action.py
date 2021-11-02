from typing import Dict

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.status_icon_hotspot import Hotspot as StatusIconHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase
from .action_state import ActionState

# import PIL.Image
# import PIL.ImageDraw


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
        offset,
    ):
        super().__init__(
            interval=interval, size=size, mode=mode, config=config, offset=offset
        )

        self.get_state_method = get_state_method
        self.set_state_method = set_state_method

        self.status_icon_hotspot = StatusIconHotspot(
            interval=0.5,
            mode=mode,
            size=(24, 24),
        )

        if self.get_state_method() == "Enabled":
            self.action_state = ActionState.ENABLED
        else:
            self.action_state = ActionState.DISABLED

        self.hotspots: Dict = {
            (self.size[0] - 24, int((self.size[1] - 24) / 2)): [
                self.status_icon_hotspot
            ],
            (1, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    size=(self.short_section_width, size[1]),
                    image_path=get_image_file_path(f"settings/icons/status/{icon}.png"),
                ),
            ],
            (int(self.width / 4), 0): [
                TextHotspot(
                    interval=interval,
                    mode=mode,
                    size=(self.width - int(self.width / 4), size[1]),
                    text="SSH",
                    font_size=14,
                )
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
        if self.get_state_method() == "Enabled":
            self.action_state = ActionState.ENABLED
        else:
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
