import logging
from math import ceil, floor

import PIL.Image
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ..pages.templates.action.state import ActionState
from ..state import Speeds
from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


def unknown_image(size):
    image = PIL.Image.new("1", size)
    center = (image.width / 2, image.height / 2)

    draw = PIL.ImageDraw.Draw(image)
    draw.ellipse(
        xy=[(0, 0), (image.width - 1, image.height - 1)],
        fill="white",
    )
    draw.text(
        xy=center,
        text="?",
        fill="black",
        font=MiniscreenAssistant("1", size).get_recommended_font(size=22),
        anchor="mm",
    )
    return image


def tick_image(size, scale, line_width):
    image = PIL.Image.new("1", size)

    center = (image.width / 2, image.height / 2)
    internal_rect_size = (scale * image.width, scale * image.height)
    internal_square_top_left = (
        image.width * (1 - scale) / 2 - 1,
        image.height * (1 - scale) / 2 - 1,
    )

    tick_top_right_x = internal_square_top_left[0] + internal_rect_size[0] + 1
    tick_top_left_y = internal_square_top_left[1] + internal_rect_size[1] * 5 / 8
    joint_xy = (
        center[0] - internal_rect_size[0] / 4,
        center[1] + internal_rect_size[1] / 2,
    )

    draw = PIL.ImageDraw.Draw(image)
    draw.ellipse(
        xy=[(0, 0), (image.width - 1, image.height - 1)],
        fill="white",
    )

    for xy in [
        joint_xy + (tick_top_right_x, internal_square_top_left[1]),
        joint_xy + (internal_square_top_left[0], tick_top_left_y),
    ]:
        draw.line(
            xy=xy,
            width=line_width,
            fill="black",
            joint="curve",
        )
    draw.ellipse(
        xy=[
            (joint_xy[0] - line_width / 2, joint_xy[1] - line_width / 2),
            (joint_xy[0] + line_width / 2, joint_xy[1] + line_width / 2),
        ],
        fill="black",
    )
    return image


def cross_image(size, scale, line_width):
    image = PIL.Image.new("1", size)

    internal_rect_size = (scale * image.width, scale * image.height)
    internal_square_top_left = (
        int(image.width * (1 - scale) / 2 - 1),
        int(image.height * (1 - scale) / 2 - 1),
    )
    internal_square_bottom_right = (
        internal_square_top_left[0] + internal_rect_size[0] + 1,
        internal_square_top_left[1] + internal_rect_size[1] + 1,
    )

    draw = PIL.ImageDraw.Draw(image)
    draw.ellipse(
        xy=[(0, 0), (image.width - 1, image.height - 1)],
        fill="white",
    )
    for xy in [
        internal_square_top_left + internal_square_bottom_right,
        (internal_square_top_left[0], internal_square_bottom_right[1])
        + (internal_square_bottom_right[0], internal_square_top_left[1]),
    ]:
        draw.line(xy=xy, width=line_width, fill="black")
    return image


def processing_image(size, frame_number):
    image = PIL.Image.new("1", size)

    circle_size = max(2, floor(image.width / 8))
    center = (image.width / 2, image.height / 2)
    off_left = (center[0] / 2, center[1])
    off_right = (center[0] * 3 / 2, center[1])

    draw = PIL.ImageDraw.Draw(image)
    draw.ellipse(
        xy=[(0, 0), (image.width - 1, image.height - 1)],
        fill="white",
    )
    for index, dot in enumerate([off_left, center, off_right]):
        if index > frame_number:
            break

        draw.ellipse(
            xy=[
                (
                    int(dot[0] - floor(circle_size / 2)),
                    int(dot[1] - floor(circle_size / 2)),
                ),
                (
                    int(dot[0] + floor(circle_size / 2)),
                    int(dot[1] + floor(circle_size / 2)),
                ),
            ],
            fill="black",
        )
    return image


def submit_image(size, scale):
    image = PIL.Image.new("1", size)
    internal_rect_size = (int(scale * image.width), int(scale * image.height))
    # offset top left to have center of triangle be center of image
    internal_square_top_left = (
        floor(image.width * (1 - scale) / 2),
        ceil(image.height * (1 - scale) / 2),
    )
    internal_square_bottom_left = (
        internal_square_top_left[0],
        internal_square_top_left[1] + internal_rect_size[0],
    )
    internal_square_middle_right = (
        internal_square_top_left[0] + internal_rect_size[0],
        ceil(internal_square_top_left[1] + internal_rect_size[1] / 2),
    )
    draw = PIL.ImageDraw.Draw(image)
    draw.ellipse(
        xy=[(0, 0), (image.width - 1, image.height - 1)],
        fill="white",
    )
    draw.polygon(
        xy=[
            internal_square_top_left,
            internal_square_bottom_left,
            internal_square_middle_right,
        ],
        fill="black",
    )
    return image


class Hotspot(HotspotBase):
    def __init__(self, size, interval=Speeds.ACTION_STATE_UPDATE.value):
        super().__init__(interval=interval, size=size)

        self.processing_frame_no = 0

        self.MAX_PROCESSING_STEPS = 3
        self.status_images = {
            ActionState.UNKNOWN: unknown_image(size),
            ActionState.ENABLED: tick_image(size, scale=0.5, line_width=3),
            ActionState.DISABLED: cross_image(size, scale=0.5, line_width=3),
            ActionState.PROCESSING: {
                frame_number: processing_image(size, frame_number=frame_number)
                for frame_number in range(self.MAX_PROCESSING_STEPS)
            },
            ActionState.SUBMIT: submit_image(size, scale=0.5),
        }

        self._action_state = ActionState.UNKNOWN

    @property
    def action_state(self):
        return self._action_state

    @action_state.setter
    def action_state(self, state):
        if self.action_state != ActionState.PROCESSING:
            self.processing_frame_no = 0

        self._action_state = state

    @property
    def status_image(self):
        if self.action_state == ActionState.PROCESSING:
            self.processing_frame_no = (
                self.processing_frame_no + 1
            ) % self.MAX_PROCESSING_STEPS
            return self.status_images[self.action_state][self.processing_frame_no]
        return self.status_images[self.action_state]

    def render(self, image):
        image.paste(self.status_image)
