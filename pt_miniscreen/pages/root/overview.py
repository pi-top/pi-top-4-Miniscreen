import logging
from math import ceil

from pitop.battery import Battery
from pitop.common.formatting import is_url
from pitop.common.sys_info import get_internal_ip

from pt_miniscreen.core import Hotspot
from pt_miniscreen.core.hotspots.image import Image
from pt_miniscreen.core.hotspots.marquee_text import MarqueeText
from pt_miniscreen.core.hotspots.text import Text
from pt_miniscreen.core.utils import apply_layers, layer, rectangle
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)

BATTERY_SIZE = (48, 22)  # must match image size
MAX_CAPACITY_SIZE = (38, 14)  # must match size of inner rectangle of charging image
BATTERY_LEFT = 9
CAPACITY_LEFT_MARGIN = 4  # must match left margin for capacity in charging image
CAPACITY_LEFT = BATTERY_LEFT + CAPACITY_LEFT_MARGIN

CAPACITY_FONT_SIZE = 16
CAPACITY_TEXT_SIZE = (40, CAPACITY_FONT_SIZE)
CAPACITY_TEXT_LEFT_MARGIN = 5
CAPACITY_TEXT_LEFT = BATTERY_LEFT + BATTERY_SIZE[0] + CAPACITY_TEXT_LEFT_MARGIN

IP_ICON_SIZE = (12, 30)
IP_ICON_LEFT = BATTERY_LEFT
IP_ICON_MARGIN_RIGHT = 5
IP_FONT_SIZE = 10
IP_TEXT_SIZE = (75, IP_FONT_SIZE)
IP_TEXT_LEFT = IP_ICON_LEFT + IP_ICON_SIZE[0] + IP_ICON_MARGIN_RIGHT

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

    capacity_width = int(MAX_CAPACITY_SIZE[0] * battery.capacity / 100)
    return (capacity_width, MAX_CAPACITY_SIZE[1])


def get_battery_image_path():
    return get_image_file_path(
        "sys_info/battery_shell_charging.png"
        if cable_connected()
        else "sys_info/battery_shell_empty.png"
    )


def get_ip():
    for interface in ("wlan0", "eth0", "ptusb0", "lo"):
        ip_address = get_internal_ip(interface)
        if is_url("http://" + ip_address):
            return ip_address

    return "No IP address"


def offset_pos_for_vertical_center(page_height, height: int) -> int:
    return int((page_height - height) / 2)


class OverviewPage(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, initial_state={"capacity_size": get_capacity_size()})

        self.battery_image = self.create_hotspot(
            Image,
            image_path=get_battery_image_path(),
        )

        self.capacity_text = self.create_hotspot(
            Text,
            text=get_capacity_text(),
            font_size=CAPACITY_FONT_SIZE,
        )

        self.ip_icon = self.create_hotspot(
            Image,
            image_path=get_image_file_path("sys_info/networking/antenna.png"),
        )

        self.ip_text = self.create_hotspot(
            MarqueeText,
            get_text=get_ip,
            get_text_interval=3,
            font_size=IP_FONT_SIZE,
        )

        # setup battery callbacks
        battery.on_capacity_change = lambda _: self.update_battery_properties()
        battery.when_charging = self.update_battery_properties
        battery.when_full = self.update_battery_properties
        battery.when_discharging = self.update_battery_properties

    # use proxy and __del__ instead of unimplemented cleanup method
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
        CAPACITY_TEXT_TOP = BATTERY_TOP + 4
        IP_ICON_TOP = BATTERY_TOP + BATTERY_SIZE[1] + ROW_SPACING
        IP_TEXT_TOP = IP_ICON_TOP + ceil((IP_ICON_SIZE[0] - IP_FONT_SIZE) / 2)

        BATTERY_POS = (BATTERY_LEFT, BATTERY_TOP)
        CAPACITY_POS = (CAPACITY_LEFT, CAPACITY_TOP)
        CAPACITY_TEXT_POS = (CAPACITY_TEXT_LEFT, CAPACITY_TEXT_TOP)
        IP_ICON_POS = (IP_ICON_LEFT, IP_ICON_TOP)
        IP_TEXT_POS = (IP_TEXT_LEFT, IP_TEXT_TOP)

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
                layer(self.ip_icon.render, size=IP_ICON_SIZE, pos=IP_ICON_POS),
                layer(self.ip_text.render, size=IP_TEXT_SIZE, pos=IP_TEXT_POS),
            ],
        )
