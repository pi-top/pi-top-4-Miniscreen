from pitop.battery import Battery

from pt_miniscreen.widgets.common import (
    draw_text, get_image_file_path, BaseSnapshot, ImageComponent
)


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)
        self.width = width
        self.height = height
        self.mode = mode
        self.battery_image = ImageComponent(
            device_mode=self.mode,
            width=self.width,
            height=self.height,
            image_path=get_image_file_path("sys_info/battery_shell_empty.png"),
            loop=False,
        )

        self.battery = Battery()
        # TODO: do initial query, then handle updates via battery class's internal subscribe client

    def draw_battery_percentage(self, draw, width, height):
        try:
            percentage = int(self.battery.capacity)
        except ValueError:
            percentage = 0

        # Magic numbers are used because the images assets are same as the page
        # so can't be used to get relative values
        top_margin = 25
        bottom_margin = 38
        left_margin = 14
        bar_width = left_margin + ((50 - left_margin) * (percentage / 100))

        draw.rectangle(
            (left_margin, top_margin) + (bar_width, bottom_margin),
            "white",
            "white"
        )

    def render(self, draw, width, height):
        if self.battery.is_charging or self.battery.is_full:
            self.battery_image = ImageComponent(
                device_mode=self.mode,
                width=self.width,
                height=self.height,
                image_path=get_image_file_path(
                    "sys_info/battery_shell_charging.png"),
                loop=False
            )
        else:
            self.battery_image = ImageComponent(
                device_mode=self.mode,
                width=self.width,
                height=self.height,
                image_path=get_image_file_path(
                    "sys_info/battery_shell_empty.png"),
                loop=False
            )
            self.draw_battery_percentage(draw, width, height)

        self.battery_image.render(draw)

        x_margin = 69
        y_margin = 21
        if self.battery.capacity is None:
            battery_capacity_text = "Unknown"
        else:
            battery_capacity_text = str(self.battery.capacity) + "%"
        draw_text(
            draw, xy=(
                x_margin, y_margin), text=battery_capacity_text, font_size=18
        )
