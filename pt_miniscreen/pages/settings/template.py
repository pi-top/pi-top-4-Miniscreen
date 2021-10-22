from PIL import Image

from ...utils import get_image_file_path
from ..widgets.common import ActionState, BaseSnapshot

status_images = {
    "off": Image.open(get_image_file_path("settings/status/off.png")),
    "on": Image.open(get_image_file_path("settings/status/on.png")),
    "processing-1": Image.open(get_image_file_path("settings/status/processing-1.png")),
    "processing-2": Image.open(get_image_file_path("settings/status/processing-2.png")),
    "processing-3": Image.open(get_image_file_path("settings/status/processing-3.png")),
    "unknown": Image.open(get_image_file_path("settings/status/unknown.png")),
}


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.width = width
        self.height = height
        self.mode = mode
        self.type = data.get("type")
        self.get_state_method = data.get("get_state_method")

        icon_image_dir = "status" if self.is_status_type else "full"
        self.icon_image = Image.open(
            get_image_file_path(f"settings/icons/{icon_image_dir}/{self.type}.png")
        )

        self.action_state = ActionState.UNKNOWN
        self.processing_icon_frame = 0
        self.initialised = False

    @property
    def is_status_type(self):
        return callable(self.get_state_method)

    def reset(self):
        self.action_state = ActionState.UNKNOWN
        self.initialised = False
        self.processing_icon_frame = 0

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

    @property
    def status_image(self):
        if self.action_state == ActionState.PROCESSING:
            image = f"processing-{self.processing_icon_frame + 1}"

        elif self.action_state == ActionState.UNKNOWN:
            image = "unknown"

        elif self.action_state == ActionState.ENABLED:
            image = "on"

        else:
            image = "off"

        return status_images[image]

    def render(self, draw, width, height):
        self.update_state()

        draw.bitmap(
            xy=(0, 0),
            bitmap=self.icon_image,
            fill="white",
        )

        if self.is_status_type:
            draw.bitmap(
                xy=(0, 0),
                bitmap=self.status_image,
                fill="white",
            )
