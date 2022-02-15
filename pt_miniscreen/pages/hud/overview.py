# This is currently a copy of the battery page
# Modify this file to build the final overview page

import logging

from pitop.battery import Battery

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.image import Hotspot as ImageHotspot
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

FONT_SIZE = 16
TEXT_SIZE = (40, FONT_SIZE)
TEXT_TOP = 25
TEXT_LEFT_MARGIN = 5
TEXT_LEFT = BATTERY_LEFT + BATTERY_SIZE[0] + TEXT_LEFT_MARGIN

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


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size)

        self.text_hotspot = TextHotspot(
            size=TEXT_SIZE,
            text=get_capacity_text(),
            font_size=FONT_SIZE,
            anchor="lt",
            xy=(0, 0),
        )

        self.battery_hotspot = ImageHotspot(
            size=BATTERY_SIZE,
            image_path=get_battery_image_path(),
        )

        self.capacity_hotspot = RectangleHotspot(
            size=CAPACITY_SIZE,
            bounding_box=get_capacity_bounding_box(),
        )

        self.hotspot_instances = [
            HotspotInstance(
                self.battery_hotspot,
                (
                    BATTERY_LEFT,
                    self.offset_pos_for_vertical_center(BATTERY_SIZE[1]),
                ),
            ),
            HotspotInstance(
                self.capacity_hotspot,
                (
                    CAPACITY_LEFT,
                    self.offset_pos_for_vertical_center(CAPACITY_SIZE[1]),
                ),
            ),
            HotspotInstance(self.text_hotspot, (TEXT_LEFT, TEXT_TOP)),
        ]

        # setup battery callbacks
        battery.on_capacity_change = lambda _: self.update_hotspots_properties()
        battery.when_charging = self.update_hotspots_properties
        battery.when_full = self.update_hotspots_properties
        battery.when_discharging = self.update_hotspots_properties

    def cleanup(self):
        battery.on_capacity_change = None
        battery.when_charging = None
        battery.when_full = None
        battery.when_discharging = None

    def update_hotspots_properties(self):
        self.text_hotspot.text = get_capacity_text()
        self.battery_hotspot.image_path = get_battery_image_path()
        self.capacity_hotspot.bounding_box = get_capacity_bounding_box()
