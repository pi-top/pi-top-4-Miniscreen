import logging

from pitop.battery import Battery

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.image import Hotspot as ImageHotspot
from ...hotspots.templates.rectangle import Hotspot as RectangleHotspot
from ...hotspots.templates.text import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase

logger = logging.getLogger(__name__)

FONT_SIZE = 16
ICON_HEIGHT = 22
RECTANGLE_HOTSPOT_SIZE = (37, 14)
BATTERY_LEFT_MARGIN = 10
TEXT_LEFT_POSITION = 60
CAPACITY_RECTANGLE_LEFT_OFFSET = 4
CAPACITY_RECTANGLE_LEFT_MARGIN = BATTERY_LEFT_MARGIN + CAPACITY_RECTANGLE_LEFT_OFFSET

# battery lives to the end of the process so we must create it globally to avoid
# memory leaks
battery = Battery()


class Page(PageBase):
    def __init__(self, size):
        self.cable_connected = battery.is_charging or battery.is_full
        try:
            self.capacity = battery.capacity
        except Exception:
            self.capacity = 0

        super().__init__(size)
        self.reset()

    def cleanup(self):
        battery.on_capacity_change = None
        battery.when_charging = None
        battery.when_full = None
        battery.when_discharging = None

    def reset(self):
        self.text_hotspot = TextHotspot(
            size=(self.short_section_width, FONT_SIZE),
            text=f"{self.capacity}%",
            font_size=FONT_SIZE,
            anchor="lt",
            xy=(0, 0),
        )

        self.battery_base_hotspot = ImageHotspot(
            size=(self.short_section_width, ICON_HEIGHT),
            image_path=None,
        )

        self.rectangle_hotspot = RectangleHotspot(
            size=RECTANGLE_HOTSPOT_SIZE,
            bounding_box=(0, 0, 0, 0),
        )

        text_hotspot_pos = (
            TEXT_LEFT_POSITION,
            self.offset_pos_for_vertical_center(self.text_hotspot.text_size[1]),
        )
        battery_hotspot_pos = (
            BATTERY_LEFT_MARGIN,
            self.offset_pos_for_vertical_center(ICON_HEIGHT),
        )
        rectangle_hotspot_pos = (
            CAPACITY_RECTANGLE_LEFT_MARGIN,
            self.offset_pos_for_vertical_center(RECTANGLE_HOTSPOT_SIZE[1]),
        )

        self.hotspot_instances = [
            HotspotInstance(self.battery_base_hotspot, battery_hotspot_pos),
            HotspotInstance(self.rectangle_hotspot, rectangle_hotspot_pos),
            HotspotInstance(self.text_hotspot, text_hotspot_pos),
        ]

        self.update_hotspots_properties()
        self.setup_events()

    def update_hotspots_properties(self):
        text = "Unknown"
        if self.capacity is not None:
            text = f"{self.capacity}%"
        self.text_hotspot.text = text

        image_path = get_image_file_path("sys_info/battery_shell_empty.png")
        if self.cable_connected:
            image_path = get_image_file_path("sys_info/battery_shell_charging.png")
        self.battery_base_hotspot.image_path = image_path

        bounding_box = (0, 0, 0, 0)
        if not self.cable_connected:
            bar_width = int(self.rectangle_hotspot.size[0] * self.capacity / 100)
            bounding_box = (0, 0, bar_width, self.rectangle_hotspot.size[1])
        self.rectangle_hotspot.bounding_box = bounding_box

    def setup_events(self):
        def update_capacity(capacity):
            self.capacity = capacity
            self.update_hotspots_properties()

        def update_charging_state(state):
            self.cable_connected = state in ("charging", "full")
            self.update_hotspots_properties()

        battery.on_capacity_change = update_capacity
        battery.when_charging = lambda: update_charging_state("charging")
        battery.when_full = lambda: update_charging_state("full")
        battery.when_discharging = lambda: update_charging_state("discharging")
