import logging
import threading
from enum import Enum, auto
from typing import Callable, Optional

from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import Image, Text
from pt_miniscreen.components.mixins import Actionable
from pt_miniscreen.core.utils import apply_layers, layer, offset_to_center
from pt_miniscreen.utils import get_image_file_path

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


class ActionPage(Component, Actionable):
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

        action_state = ActionState.PROCESSING
        super().__init__(**kwargs, initial_state={"action_state": action_state})

        self.text_component = self.create_child(
            Text,
            text=text,
            font_size=font_size,
            align="right",
            vertical_align="center",
        )
        self.status_icon_component = self.create_child(
            Image, image_path=get_image_file_path(image_paths[action_state])
        )

        # get initial state in background
        threading.Thread(target=self._update_action_state, daemon=True).start()

    def _calculate_action_state(self):
        if not callable(self._get_enabled_state):
            return ActionState.IDLE

        if self._get_enabled_state() == "Enabled":
            return ActionState.ENABLED

        return ActionState.DISABLED

    def _update_action_state(self):
        self.state.update({"action_state": self._calculate_action_state()})

    def on_state_change(self, previous_state):
        if self.state["action_state"] != previous_state["action_state"]:
            self.status_icon_component.state.update(
                {"image_path": image_paths[self.state["action_state"]]}
            )

    def _perform_action(self):
        try:
            logger.info(f"{self} starting action")
            self._action()
            self._update_action_state()
            logger.info(f"{self} finished action")

        except Exception as e:
            self.state.update({"action_state": ActionState.UNKNOWN})
            logger.error(f"{self} failed to start action: {e}")

    def perform_action(self) -> None:
        if self.state["action_state"] == ActionState.PROCESSING or not callable(
            self._action
        ):
            return

        self.state.update({"action_state": ActionState.PROCESSING})
        threading.Thread(target=self._perform_action, daemon=True).start()

    def render(self, image):
        FIRST_COLUMN_POS = 5
        FIRST_COLUMN_WIDTH = 55
        COLUMN_GAP = 8
        SECOND_COLUMN_POS = FIRST_COLUMN_POS + FIRST_COLUMN_WIDTH + COLUMN_GAP
        STATUS_ICON_SIZE = 24
        THIRD_COLUMN_WIDTH = STATUS_ICON_SIZE

        return apply_layers(
            image,
            [
                layer(
                    self.text_component.render,
                    size=(FIRST_COLUMN_WIDTH, image.size[1]),
                    pos=(FIRST_COLUMN_POS, 0),
                ),
                layer(
                    self.status_icon_component.render,
                    size=(THIRD_COLUMN_WIDTH, STATUS_ICON_SIZE),
                    pos=(
                        SECOND_COLUMN_POS,
                        offset_to_center(image.height, STATUS_ICON_SIZE),
                    ),
                ),
            ],
        )
