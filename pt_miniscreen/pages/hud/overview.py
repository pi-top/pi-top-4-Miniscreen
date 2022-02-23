import logging
from math import ceil

from pitop.battery import Battery
from pitop.common.formatting import is_url
from pitop.common.sys_info import get_internal_ip

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.image import Hotspot as ImageHotspot
from ...hotspots.templates.marquee_dynamic_text import (
    Hotspot as DynamicMarqueeTextHotspot,
)
from ...hotspots.templates.rectangle import Hotspot as RectangleHotspot
from ...hotspots.templates.text import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

logger = logging.getLogger(__name__)

BATTERY_SIZE = (48, 22)  # must match image size
CAPACITY_SIZE = (37, 14)  # must match size of inner rectangle of charging image
BATTERY_LEFT = 10
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


def get_capacity_bounding_box():
    if cable_connected():
        return (0, 0, 0, 0)

    capacity_width = int(CAPACITY_SIZE[0] * battery.capacity / 100)
    return (0, 0, capacity_width, CAPACITY_SIZE[1])


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


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size)

        self.battery_hotspot = ImageHotspot(
            size=BATTERY_SIZE,
            image_path=get_battery_image_path(),
        )

        self.capacity_hotspot = RectangleHotspot(
            size=CAPACITY_SIZE,
            bounding_box=get_capacity_bounding_box(),
        )

        self.capacity_text_hotspot = TextHotspot(
            size=CAPACITY_TEXT_SIZE,
            text=get_capacity_text(),
            font_size=CAPACITY_FONT_SIZE,
        )

        self.ip_icon_hotspot = ImageHotspot(
            size=IP_ICON_SIZE,
            image_path=get_image_file_path("sys_info/networking/antenna.png"),
        )

        self.ip_text_hotspot = DynamicMarqueeTextHotspot(
            size=IP_TEXT_SIZE,
            text=get_ip,
            font_size=IP_FONT_SIZE,
            update_interval=3,
        )

        BATTERY_OFFSET = -10  # offset from the vertical center of the page
        BATTERY_TOP = (
            self.offset_pos_for_vertical_center(BATTERY_SIZE[1]) + BATTERY_OFFSET
        )
        CAPACITY_TOP = (
            self.offset_pos_for_vertical_center(CAPACITY_SIZE[1]) + BATTERY_OFFSET
        )
        CAPACITY_TEXT_TOP = BATTERY_TOP + 4
        IP_ICON_TOP = BATTERY_TOP + BATTERY_SIZE[1] + ROW_SPACING
        IP_TEXT_TOP = IP_ICON_TOP + ceil((IP_ICON_SIZE[0] - IP_FONT_SIZE) / 2)

        BATTERY_POS = (BATTERY_LEFT, BATTERY_TOP)
        CAPACITY_POS = (CAPACITY_LEFT, CAPACITY_TOP)
        CAPACITY_TEXT_POS = (CAPACITY_TEXT_LEFT, CAPACITY_TEXT_TOP)
        IP_ICON_POS = (IP_ICON_LEFT, IP_ICON_TOP)
        IP_TEXT_POS = (IP_TEXT_LEFT, IP_TEXT_TOP)

        self.hotspot_instances = [
            HotspotInstance(self.battery_hotspot, BATTERY_POS),
            HotspotInstance(self.capacity_hotspot, CAPACITY_POS),
            HotspotInstance(self.capacity_text_hotspot, CAPACITY_TEXT_POS),
            HotspotInstance(self.ip_icon_hotspot, IP_ICON_POS),
            HotspotInstance(self.ip_text_hotspot, IP_TEXT_POS),
        ]

        # setup battery callbacks
        battery.on_capacity_change = lambda _: self.update_battery_properties()
        battery.when_charging = self.update_battery_properties
        battery.when_full = self.update_battery_properties
        battery.when_discharging = self.update_battery_properties

    def cleanup(self):
        self._ip_update_stop_event.set()
        battery.on_capacity_change = None
        battery.when_charging = None
        battery.when_full = None
        battery.when_discharging = None

    def update_battery_properties(self):
        self.battery_hotspot.image_path = get_battery_image_path()
        self.capacity_hotspot.bounding_box = get_capacity_bounding_box()
        self.capacity_text_hotspot.text = get_capacity_text()
