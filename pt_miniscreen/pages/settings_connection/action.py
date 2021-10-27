from enum import Enum
from typing import Dict

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.processing_icon_hotspot import Hotspot as ProcessingIconHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

# import PIL.Image
# import PIL.ImageDraw


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

        self._action_state = ActionState.UNKNOWN

        # TODO:
        #   * image hotspot for 'unknown', 'on' and 'off'
        #   * update hotspot in a given position when the state changes
        processing_icon_hotspot = ProcessingIconHotspot(
            interval=0.5,
            mode=mode,
            size=(24, 24),
        )

        self.hotspots: Dict = {
            (int(self.size[0] * 3 / 4), int(self.size[1] / 4)): [
                processing_icon_hotspot
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
        return self._action_state

    @action_state.setter
    def action_state(self, state: ActionState):
        if state == ActionState.UNKNOWN:
            # If unknown state is entered into after initialisation
            # stay in that state until page is reset
            return

        if state == ActionState.PROCESSING:
            # Update state of processing hotspot
            pass
        self._action_state = state

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
        self.action_state = ActionState.FINISHED_PROCESSING


# class Page(PageBase):
#     def __init__(
#         self, interval, size, mode, config, get_state_method, set_state_method, icon
#     ):
#         super().__init__(interval=interval, size=size, mode=mode, config=config)

#         self.get_state_method = get_state_method
#         self.set_state_method = set_state_method

#         self.icon_img_path = get_image_file_path(f"settings/icons/status/{icon}.png")
#         self.icon_image = PIL.Image.open(self.icon_img_path)

#         self.action_state = ActionState.UNKNOWN
#         self.status_img_path = self.get_status_image_path()
#         self.status_image = PIL.Image.open(self.status_img_path)
#         self.processing_icon_frame = 0
#         self.initialised = False

#     def reset(self):
#         self.action_state = ActionState.UNKNOWN
#         self.status_img_path = self.get_status_image_path()
#         self.status_image = PIL.Image.open(self.status_img_path)
#         self.initialised = False
#         self.processing_icon_frame = 0

#     @property
#     def is_status_type(self):
#         return callable(self.get_state_method)

#     def update_state(self):
#         if not self.is_status_type:
#             return

#         if self.action_state == ActionState.PROCESSING:
#             self.processing_icon_frame = (self.processing_icon_frame + 1) % 3
#             return

#         if self.action_state == ActionState.UNKNOWN:
#             # If unknown state is entered into after initialisation
#             # stay in that state until page is reset
#             if self.initialised:
#                 return

#         if self.get_state_method() == "Enabled":
#             self.action_state = ActionState.ENABLED
#         else:
#             self.action_state = ActionState.DISABLED

#         self.initialised = True

#     def get_status_image_path(self):
#         if self.action_state == ActionState.PROCESSING:
#             img_file = f"processing-{self.processing_icon_frame + 1}"

#         elif self.action_state == ActionState.UNKNOWN:
#             img_file = "unknown"

#         elif self.action_state == ActionState.ENABLED:
#             img_file = "on"

#         else:
#             img_file = "off"

#         return get_image_file_path(f"settings/status/{img_file}.png")

#     def update_status_image(self):
#         current_status_img_path = self.get_status_image_path()
#         if self.status_img_path != current_status_img_path:
#             self.status_img_path = current_status_img_path
#             self.status_image = PIL.Image.open(self.status_img_path)

#     def render(self, image):
#         self.update_state()
#         self.update_status_image()

#         PIL.ImageDraw.Draw(image).bitmap(
#             xy=(0, 0),
#             bitmap=self.icon_image,
#             fill="white",
#         )

#         if self.is_status_type:
#             PIL.ImageDraw.Draw(image).bitmap(
#                 xy=(0, 0),
#                 bitmap=self.status_image,
#                 fill="white",
#             )
