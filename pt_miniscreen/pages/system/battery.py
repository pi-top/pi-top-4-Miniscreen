import logging

from pitop.battery import Battery

from pt_miniscreen.core import Hotspot
from pt_miniscreen.core.utils import apply_layers, layer, rectangle
from pt_miniscreen.hotspots.image import ImageHotspot
from pt_miniscreen.hotspots.text import TextHotspot
from pt_miniscreen.utils import get_image_file_path, offset_to_center

logger = logging.getLogger(__name__)

BATTERY_SIZE = (48, 22)  # must match image size
CAPACITY_SIZE = (38, 14)  # must match size of inner rectangle of charging image
BATTERY_LEFT = 9
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


def get_capacity_size():
    if cable_connected():
        return (0, 0)

    capacity_width = int(CAPACITY_SIZE[0] * battery.capacity / 100)
    return (capacity_width, CAPACITY_SIZE[1])


def get_battery_image_path():
    return get_image_file_path(
        "sys_info/battery_shell_charging.png"
        if cable_connected()
        else "sys_info/battery_shell_empty.png"
    )


class BatteryPage(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, initial_state={"capacity_size": get_capacity_size()})

        self.battery_image = self.create_hotspot(
            ImageHotspot,
            image_path=get_battery_image_path(),
        )

        self.capacity_text = self.create_hotspot(
            TextHotspot,
            text=get_capacity_text(),
            font_size=FONT_SIZE,
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
        BATTERY_TOP = offset_to_center(image.height, BATTERY_SIZE[1])
        CAPACITY_TOP = offset_to_center(image.height, CAPACITY_SIZE[1])
        TEXT_TOP = BATTERY_TOP + 4

        BATTERY_POS = (BATTERY_LEFT, BATTERY_TOP)
        CAPACITY_POS = (CAPACITY_LEFT, CAPACITY_TOP)
        TEXT_POS = (TEXT_LEFT, TEXT_TOP)

        return apply_layers(
            image,
            [
                layer(self.battery_image.render, size=BATTERY_SIZE, pos=BATTERY_POS),
                layer(rectangle, size=self.state["capacity_size"], pos=CAPACITY_POS),
                layer(
                    self.capacity_text.render,
                    size=TEXT_SIZE,
                    pos=TEXT_POS,
                ),
            ],
        )
