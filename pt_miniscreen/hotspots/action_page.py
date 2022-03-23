import logging
import threading
from enum import Enum, auto
from typing import Callable, Optional

from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.image import ImageHotspot
from pt_miniscreen.hotspots.text import TextHotspot
from pt_miniscreen.utils import get_image_file_path, offset_to_center

logger = logging.getLogger(__name__)


class ActionState(Enum):
    UNKNOWN = auto()
    PROCESSING = auto()
    ENABLED = auto()
    DISABLED = auto()
    IDLE = auto()


image_paths = {
    ActionState.UNKNOWN: get_image_file_path("status/unknown.png"),
    ActionState.ENABLED: get_image_file_path("status/enabled.png"),
    ActionState.DISABLED: get_image_file_path("status/disabled.png"),
    ActionState.PROCESSING: get_image_file_path("status/processing.gif"),
    ActionState.IDLE: get_image_file_path("status/idle.png"),
}


class ActionPage(Hotspot):
    def __init__(
        self,
        text: str,
        action: Callable,
        get_enabled_state: Optional[Callable] = None,
        font_size=14,
        **kwargs,
    ) -> None:
        self._action = action
        self._get_enabled_state = get_enabled_state

        # def reset_if_processing():
        #     if self.action_state == ActionState.PROCESSING:
        #         self.reset()

        # subscribe(AppEvent.ACTION_TIMEOUT, reset_if_processing)
        # subscribe(AppEvent.ACTION_FINISH, reset_if_processing)

        action_state = self._calculate_action_state()
        super().__init__(**kwargs, initial_state={"action_state": action_state})

        self.text_hotspot = self.create_hotspot(
            TextHotspot,
            text=text,
            font_size=font_size,
            align="right",
            vertical_align="center",
        )
        self.status_icon_hotspot = self.create_hotspot(
            ImageHotspot, image_path=get_image_file_path(image_paths[action_state])
        )

    def _calculate_action_state(self):
        if not callable(self._get_enabled_state):
            return ActionState.IDLE

        if self._get_enabled_state() == "Enabled":
            return ActionState.ENABLED

        return ActionState.DISABLED

    def on_state_change(self, previous_state):
        if self.state["action_state"] != previous_state["action_state"]:
            self.status_icon_hotspot.state.update(
                {"image_path": image_paths[self.state["action_state"]]}
            )

    def _perform_action(self):
        try:
            self._action()
            logger.debug(f"{self} calculating final action state")
            self.state.update({"action_state": self._calculate_action_state()})
        except Exception as e:
            self.state.update({"action_state": ActionState.UNKNOWN})
            logger.error(f"Failed to start action: {e}")

    def perform_action(self) -> None:
        logger.debug(f"{self} performing action")
        if self.state["action_state"] == ActionState.PROCESSING or not callable(
            self._action
        ):
            logger.debug(f"{self} bailing")
            return

        self.state.update({"action_state": ActionState.PROCESSING})
        logger.debug(f"{self} processing")
        threading.Thread(target=self._perform_action, daemon=True).start()

    def render(self, image):
        FIRST_COLUMN_POS = 7
        FIRST_COLUMN_WIDTH = 52
        COLUMN_GAP = 8
        SECOND_COLUMN_POS = FIRST_COLUMN_POS + FIRST_COLUMN_WIDTH + COLUMN_GAP
        STATUS_ICON_SIZE = 24
        THIRD_COLUMN_WIDTH = STATUS_ICON_SIZE

        return apply_layers(
            image,
            [
                layer(
                    self.text_hotspot.render,
                    size=(FIRST_COLUMN_WIDTH, image.size[1]),
                    pos=(FIRST_COLUMN_POS, 0),
                ),
                layer(
                    self.status_icon_hotspot.render,
                    size=(THIRD_COLUMN_WIDTH, STATUS_ICON_SIZE),
                    pos=(
                        SECOND_COLUMN_POS,
                        offset_to_center(image.height, STATUS_ICON_SIZE),
                    ),
                ),
            ],
        )
