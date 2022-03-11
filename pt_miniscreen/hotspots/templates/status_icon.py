import logging

from pt_miniscreen.utils import get_image_file_path

from ...pages.templates.action.state import ActionState
from ...state import Speeds
from .image import Hotspot as ImageHotspot

logger = logging.getLogger(__name__)

image_paths = {
    ActionState.UNKNOWN: get_image_file_path("status/unknown.png"),
    ActionState.ENABLED: get_image_file_path("status/enabled.png"),
    ActionState.DISABLED: get_image_file_path("status/disabled.png"),
    ActionState.PROCESSING: get_image_file_path("status/processing.gif"),
    ActionState.IDLE: get_image_file_path("status/idle.png"),
}


class Hotspot(ImageHotspot):
    def __init__(self, size, interval=Speeds.ACTION_STATE_UPDATE.value):
        super().__init__(
            interval=interval, size=size, image_path=image_paths[ActionState.UNKNOWN]
        )
        self._action_state = ActionState.UNKNOWN

    @property
    def action_state(self):
        return self._action_state

    @action_state.setter
    def action_state(self, state):
        self._action_state = state
        self.image_path = image_paths[state]
