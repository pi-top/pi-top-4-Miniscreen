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

        font_size = 20
        text_hotspot_pos = (int(1 / 2 * self.size[0]), 0)
        text_hotspot_size = (
            size[0] - text_hotspot_pos[0],
            size[1] - text_hotspot_pos[1],
        )
        self.text_hotspot = TextHotspot(
            interval=interval,
            mode=mode,
            size=text_hotspot_size,
            text=f"{self.capacity} %",
            font_size=font_size,
            xy=(int(text_hotspot_size[0]) / 2, int(text_hotspot_size[1]) / 2),
        )

        self.battery_base_hotspot = ImageHotspot(
            interval=interval, mode=mode, size=size, image_path=None, xy=(0, 0)
        )

        self.rectangle_hotspot = RectangleHotspot(
            interval=interval, mode=mode, size=size, bounding_box=(0, 0, 0, 0)
        )

        # self.hotspots: Dict[Tuple, List[Hotspot]] = {
        self.hotspots: Dict = {
            (0, 0): [self.battery_base_hotspot, self.rectangle_hotspot],
            text_hotspot_pos: [self.text_hotspot],
        }

        self.update_hotspots_properties()
        self.setup_events()

    def update_hotspots_properties(self):
        text = "Unknown"
        if self.capacity is not None:
            text = f"{self.capacity} %"
        self.text_hotspot.text = text

        image_path = get_image_file_path("sys_info/battery_shell_empty.png")
        if self.cable_connected:
            image_path = get_image_file_path("sys_info/battery_shell_charging.png")
        self.battery_base_hotspot.image_path = image_path

        bounding_box = (0, 0, 0, 0)
        if not self.cable_connected:
            top_margin = 25
            bottom_margin = 38
            left_margin = 14
            max_bar_width = 36
            bar_width = int(max_bar_width * self.capacity / 100)
            bar_end = left_margin + bar_width
            bounding_box = (left_margin, top_margin) + (bar_end, bottom_margin)
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


# class TextHotspot2(PageBase):
#     def __init__(self, interval, size, mode):
#         self.assistant = MiniscreenAssistant(self.mode, self.size)
#         self.battery = Battery()

#     def render(self, image):
#         battery_capacity_text = (
#             "Unknown"
#             if self.battery.capacity is None
#             else str(self.battery.capacity) + "%"
#         )

#         self.assistant.render_text(
#             image,
#             text=battery_capacity_text,
#             xy=(3 / 4 * self.size[0], 1 / 2 * self.size[1]),
#             font_size=20,
#         )


# class ImageHotspot2(PageBase):
#     def __init__(self, interval, size, mode):
#         pass

#     def draw_battery_percentage(self, image):
#         try:
#             percentage = int(self.battery.capacity)
#         except ValueError:
#             percentage = 0

#         # Magic numbers are used because the images assets are same as the page
#         # so can't be used to get relative values
#         top_margin = 25
#         bottom_margin = 38
#         left_margin = 18
#         bar_width = left_margin + ((50 - left_margin) * (percentage / 100))

#         PIL.ImageDraw.Draw(image).rectangle(
#             (left_margin, top_margin) + (bar_width, bottom_margin), "white", "white"
#         )

#     def render(self, image):
#         if self.battery.is_charging or self.battery.is_full:
#             self.battery_image = self.charging_battery_image
#         else:
#             self.battery_image = self.empty_battery_image
#             self.draw_battery_percentage(image)

#         PIL.ImageDraw.Draw(image).bitmap(
#             # Offset battery image slightly
#             xy=(4, 0),
#             bitmap=self.battery_image.convert(self.mode),
#             fill="white",
#         )
