from PIL import Image

from pt_miniscreen.widgets.common import ActionState, BaseSnapshot, get_image_file_path


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.width = width
        self.height = height
        self.mode = mode
        self.type = data.get("type")
        self.get_state_method = data.get("get_state_method")

        image_dir = "status_icons" if self.is_status_type else "full_icons"
        self.icon_img_path = get_image_file_path(
            f"settings/{image_dir}/{self.type}.png"
        )
        self.icon_image = Image.open(self.icon_img_path)

        self.action_state = ActionState.UNKNOWN
        self.status_img_path = self.get_status_image_path()
        self.status_image = Image.open(self.status_img_path)
        self.processing_icon_frame = 0
        self.initialised = False

    def reset(self):
        self.action_state = ActionState.UNKNOWN
        self.status_img_path = self.get_status_image_path()
        self.status_image = Image.open(self.status_img_path)
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
            self.status_image = Image.open(self.status_img_path)

    def set_as_processing(self):
        self.action_state = ActionState.PROCESSING

    def render(self, draw, width, height):
        self.update_state()
        self.update_status_image()

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
