from components.widgets.common_functions import draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot
from components.widgets.common_functions import get_image_file
from components.widgets.common.image_component import ImageComponent


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.gif = ImageComponent(
            image_path=get_image_file("battery_shell_empty.gif"), loop=False
        )
        self.battery_percentage = ""
        self.charging = False
        self.get_battery_info_method = data.get("method")
        self.state = None
        self.capacity = None

    def update_battery_state(self):
        self.state, self.capacity = self.self.get_battery_info_method()

        self.battery_percentage = str(self.capacity) + "%"

        charging = True if int(self.state) == 1 else False
        fully_charged = True if int(self.state) == 2 else False
        self.charging = charging or fully_charged

    def draw_battery_percentage(self, draw, width, height):
        try:
            percentage = int(self.capacity)
        except ValueError:
            percentage = 0

        # Magic numbers are used because the images assets are same as the page
        # so can't be used to get relative values
        top_margin = 25
        bottom_margin = 38
        left_margin = 14
        bar_width = left_margin + ((50 - left_margin) * (percentage / 100))

        draw.rectangle(
            (left_margin, top_margin) +
            (bar_width, bottom_margin), "white", "white"
        )

    def render(self, draw, width, height):
        self.update_battery_state()

        if self.charging:
            self.gif = ImageComponent(
                image_path=get_image_file("battery_shell_charging.gif"), loop=False
            )
        else:
            self.gif = ImageComponent(
                image_path=get_image_file("battery_shell_empty.gif"), loop=False
            )
            self.draw_battery_percentage(draw, width, height)

        self.gif.render(draw)

        x_margin = 69
        y_margin = 21
        draw_text(
            draw, xy=(
                x_margin, y_margin), text=self.battery_percentage, font_size=18
        )
