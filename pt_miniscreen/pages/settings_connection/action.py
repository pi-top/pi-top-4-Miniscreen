from enum import Enum

import PIL.Image
import PIL.ImageDraw

from ...utils import get_image_file_path
from ..base import Page as PageBase


class ActionState(Enum):
    UNKNOWN = 0
    PROCESSING = 1
    ENABLED = 2
    DISABLED = 3
    FINISHED_PROCESSING = 4


class Page(PageBase):
    def __init__(
        self, interval, size, mode, config, get_state_method, set_state_method, icon
    ):
        super().__init__(interval=interval, size=size, mode=mode, config=config)

        self.get_state_method = get_state_method
        self.set_state_method = set_state_method

        self.icon_img_path = get_image_file_path(f"settings/icons/status/{icon}.png")
        self.icon_image = PIL.Image.open(self.icon_img_path)

        self.action_state = ActionState.UNKNOWN
        self.status_img_path = self.get_status_image_path()
        self.status_image = PIL.Image.open(self.status_img_path)
        self.processing_icon_frame = 0
        self.initialised = False

    def reset(self):
        self.action_state = ActionState.UNKNOWN
        self.status_img_path = self.get_status_image_path()
        self.status_image = PIL.Image.open(self.status_img_path)
        self.initialised = False
        self.processing_icon_frame = 0

    @property
    def is_status_type(self):
        return callable(self.get_state_method)

    def update_state(self):
        if not self.is_status_type:
            return

        if self.action_state == ActionState.PROCESSING:
            self.processing_icon_frame = (self.processing_icon_frame + 1) % 3
            return

        if self.action_state == ActionState.UNKNOWN:
            # If unknown state is entered into after initialisation
            # stay in that state until page is reset
            if self.initialised:
                return

        if self.get_state_method() == "Enabled":
            self.action_state = ActionState.ENABLED
        else:
            self.action_state = ActionState.DISABLED

        self.initialised = True

    def get_status_image_path(self):
        if self.action_state == ActionState.PROCESSING:
            img_file = f"processing-{self.processing_icon_frame + 1}"

        elif self.action_state == ActionState.UNKNOWN:
            img_file = "unknown"

        elif self.action_state == ActionState.ENABLED:
            img_file = "on"

        else:
            img_file = "off"

        return get_image_file_path(f"settings/status/{img_file}.png")

    def update_status_image(self):
        current_status_img_path = self.get_status_image_path()
        if self.status_img_path != current_status_img_path:
            self.status_img_path = current_status_img_path
            self.status_image = PIL.Image.open(self.status_img_path)

    def render(self, image):
        self.update_state()
        self.update_status_image()

        PIL.ImageDraw.Draw(image).bitmap(
            xy=(0, 0),
            bitmap=self.icon_image,
            fill="white",
        )

        if self.is_status_type:
            PIL.ImageDraw.Draw(image).bitmap(
                xy=(0, 0),
                bitmap=self.status_image,
                fill="white",
            )

    def on_select_press(self):
        if callable(self.set_state_method):
            self.action_state = ActionState.PROCESSING
            self.set_state_method()
            self.action_state = ActionState.FINISHED_PROCESSING
