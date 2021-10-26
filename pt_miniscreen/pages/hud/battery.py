import logging
from typing import Dict  # , List, Tuple

from pitop.battery import Battery

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.rectangle_hotspot import Hotspot as RectangleHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import PageBase

logger = logging.getLogger(__name__)


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval, size, mode, config)
        self.interval = interval
        self.size = size
        self.mode = mode

        self.battery = Battery()
        self.cable_connected = self.battery.is_charging or self.battery.is_full
        self.capacity = 0
        try:
            self.capacity = self.battery.capacity
        except Exception:
            pass

        self.text_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=(self.long_section_width, size[1]),
            text=f"{self.capacity}%",
            font_size=19,
            xy=(self.short_section_width, size[1] / 2),
        )
        self.text_hotspot.overlay = True

        self.battery_base_hotspot = ImageHotspot(
            interval=interval,
            mode=mode,
            size=(self.short_section_width, size[1]),
            image_path=None,
        )

        self.rectangle_hotspot = RectangleHotspot(
            interval=interval, mode=mode, size=(37, 14), bounding_box=(0, 0, 0, 0)
        )
        self.rectangle_hotspot.overlay = True

        battery_left_margin = 15
        capacity_rectangle_left_offset = 4
        capacity_rectangle_left_margin = (
            battery_left_margin + capacity_rectangle_left_offset
        )
        capacity_rectangle_top_margin = 25

        # self.hotspots: Dict[Tuple, List[Hotspot]] = {
        self.hotspots: Dict = {
            (battery_left_margin, 0): [self.battery_base_hotspot],
            (capacity_rectangle_left_margin, capacity_rectangle_top_margin): [
                self.rectangle_hotspot
            ],
            (self.short_section_width, 0): [self.text_hotspot],
        }

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

        self.battery.on_capacity_change = update_capacity
        self.battery.when_charging = lambda: update_charging_state("charging")
        self.battery.when_full = lambda: update_charging_state("full")
        self.battery.when_discharging = lambda: update_charging_state("discharging")
