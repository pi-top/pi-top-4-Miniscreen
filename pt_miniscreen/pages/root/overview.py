import logging
from math import ceil

from pitop.battery import Battery
from pitop.common.sys_info import get_pi_top_ip

from pt_miniscreen.core import Component
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.core.utils import apply_layers, layer, rectangle
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)

BATTERY_SIZE = (48, 22)  # must match image size
MAX_CAPACITY_SIZE = (37, 14)  # must match size of inner rectangle of charging image
BATTERY_LEFT = 9
CAPACITY_LEFT_MARGIN = 4  # must match left margin for capacity in charging image
CAPACITY_LEFT = BATTERY_LEFT + CAPACITY_LEFT_MARGIN

CAPACITY_FONT_SIZE = 16
CAPACITY_TEXT_SIZE = (40, BATTERY_SIZE[1])
CAPACITY_TEXT_LEFT_MARGIN = 5
CAPACITY_TEXT_LEFT = BATTERY_LEFT + BATTERY_SIZE[0] + CAPACITY_TEXT_LEFT_MARGIN

IP_FONT_SIZE = 10
IP_TEXT_LEFT = BATTERY_LEFT

ROW_SPACING = 10

# battery lives to the end of the process so we must create it globally to avoid
# memory leaks
battery = Battery()


def cable_connected():
    return battery.is_charging or battery.is_full


def get_capacity_text():
    return "Unknown" if battery.capacity is None else f"{battery.capacity}%"


def get_capacity_size():
    if cable_connected():
        return (0, 0)

    capacity_width = ceil(MAX_CAPACITY_SIZE[0] * battery.capacity / 100)
    return (capacity_width, MAX_CAPACITY_SIZE[1])


def get_battery_image_path():
    return get_image_file_path(
        "sys_info/battery_shell_charging.png"
        if cable_connected()
        else "sys_info/battery_shell_empty.png"
    )


def get_ip():
    ip_address = get_pi_top_ip()
    if len(ip_address) > 0:
        return ip_address
    return "No IP address"


def offset_pos_for_vertical_center(page_height, height: int) -> int:
    return int((page_height - height) / 2)


class OverviewPage(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, initial_state={"capacity_size": get_capacity_size()})

        self.battery_image = self.create_child(
            Image,
            image_path=get_battery_image_path(),
        )

        self.capacity_text = self.create_child(
            Text,
            text=get_capacity_text(),
            font_size=CAPACITY_FONT_SIZE,
            vertical_align="center",
        )

        self.ip_text = self.create_child(
            Text,
            text=get_ip(),
            get_text=get_ip,
            get_text_interval=3,
            font_size=IP_FONT_SIZE,
            align="center",
            vertical_align="bottom",
        )

        # setup battery callbacks
        battery.on_capacity_change = lambda _: self.update_battery_properties()
        battery.when_charging = self.update_battery_properties
        battery.when_full = self.update_battery_properties
        battery.when_discharging = self.update_battery_properties

    def cleanup(self):
        battery.on_capacity_change = None
        battery.when_charging = None
        battery.when_full = None
        battery.when_discharging = None

    def update_battery_properties(self):
        self.capacity_text.state.update({"text": get_capacity_text()})
        self.battery_image.state.update({"image_path": get_battery_image_path()})
        self.state.update({"capacity_size": get_capacity_size()})

    def render(self, image):
        BATTERY_OFFSET = -10  # offset from the vertical center of the page
        BATTERY_TOP = (
            offset_pos_for_vertical_center(image.height, BATTERY_SIZE[1])
            + BATTERY_OFFSET
        )
        CAPACITY_TOP = (
            offset_pos_for_vertical_center(image.height, MAX_CAPACITY_SIZE[1])
            + BATTERY_OFFSET
        )
        IP_TEXT_TOP = BATTERY_TOP + BATTERY_SIZE[1] + ROW_SPACING

        BATTERY_POS = (BATTERY_LEFT, BATTERY_TOP)
        CAPACITY_POS = (CAPACITY_LEFT, CAPACITY_TOP)
        CAPACITY_TEXT_POS = (CAPACITY_TEXT_LEFT, BATTERY_TOP)
        IP_TEXT_POS = (0, IP_TEXT_TOP)

        return apply_layers(
            image,
            [
                layer(self.battery_image.render, size=BATTERY_SIZE, pos=BATTERY_POS),
                layer(rectangle, size=self.state["capacity_size"], pos=CAPACITY_POS),
                layer(
                    self.capacity_text.render,
                    size=CAPACITY_TEXT_SIZE,
                    pos=CAPACITY_TEXT_POS,
                ),
                layer(
                    self.ip_text.render,
                    size=(image.width, IP_FONT_SIZE),
                    pos=IP_TEXT_POS,
                ),
            ],
        )
