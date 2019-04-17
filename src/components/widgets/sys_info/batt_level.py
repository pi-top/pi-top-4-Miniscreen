from ptcommon.sys_info import get_battery_capacity, get_battery_charging_state
from components.widgets.common_functions import draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_functions import get_image_file
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(image_path=get_image_file("battery_shell_empty.gif"), loop=False)
        self.battery_percentage = ""
        self.charging = False
        self.previous_charging = False

    def update_battery_state(self):
        self.battery_percentage = get_battery_capacity()
        self.previous_charging = self.charging
        self.charging = get_battery_charging_state() == "charging"


    def draw_battery_percentage(self, draw, width, height):
        try:
            # Remove '%' for evaluating bar width
            percentage = int(self.battery_percentage[:-1])
        except ValueError:
            percentage = 0

        # Magic numbers are used because the images assets are same as the page
        # so can't be used to get relative values
        top_margin = 25
        bottom_margin = 38
        left_margin = 14
        bar_width = left_margin + ((50 - left_margin) * (percentage / 100))

        draw.rectangle(
            (left_margin, top_margin) + (bar_width, bottom_margin), "white", "white"
        )

    def render(self, draw, width, height):
        self.update_battery_state()

        self.draw_battery_percentage(draw, width, height)

        update_battery_icon = False
        if self.charging and not self.previous_charging:
            update_battery_icon = True
            self.gif = ImageComponent(image_path=get_image_file("battery_shell_charging.gif"), loop=False)
        elif not self.charging and self.previous_charging:
            update_battery_icon = True
            self.gif = ImageComponent(image_path=get_image_file("battery_shell_empty.gif"), loop=False)

        if update_battery_icon:
            self.gif.render(draw)

        x_margin = 69
        y_margin = 21
        draw_text(
            draw, xy=(x_margin, y_margin), text=self.battery_percentage, font_size=18
        )
