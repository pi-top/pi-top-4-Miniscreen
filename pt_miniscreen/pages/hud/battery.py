import PIL.Image
import PIL.ImageDraw
from pitop.battery import Battery
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...utils import get_image_file_path
from ..base import PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.empty_battery_image = PIL.Image.open(
            get_image_file_path("sys_info/battery_shell_empty.png")
        )
        self.charging_battery_image = PIL.Image.open(
            get_image_file_path("sys_info/battery_shell_charging.png")
        )
        self.battery = Battery()

    def draw_battery_percentage(self, image):
        try:
            percentage = int(self.battery.capacity)
        except ValueError:
            percentage = 0

        # Magic numbers are used because the images assets are same as the page
        # so can't be used to get relative values
        top_margin = 25
        bottom_margin = 38
        left_margin = 18
        bar_width = left_margin + ((50 - left_margin) * (percentage / 100))

        PIL.ImageDraw.Draw(image).rectangle(
            (left_margin, top_margin) + (bar_width, bottom_margin), "white", "white"
        )

    def render(self, image):
        assistant = MiniscreenAssistant(self.mode, self.size)
        # TODO: move to standard assistant function
        #
        # MiniscreenAssistant(self.mode, self.size).render_hud_icon(
        #     image,
        #     text=self.text,
        #     image_path=get_image_file_path("sys_info/battery_shell_charging.png"),
        # )

        if self.battery.is_charging or self.battery.is_full:
            self.battery_image = self.charging_battery_image
        else:
            self.battery_image = self.empty_battery_image
            self.draw_battery_percentage(image)

        PIL.ImageDraw.Draw(image).bitmap(
            # Offset battery image slightly
            xy=(4, 0),
            bitmap=self.battery_image.convert(self.mode),
            fill="white",
        )

        battery_capacity_text = (
            "Unknown"
            if self.battery.capacity is None
            else str(self.battery.capacity) + "%"
        )

        assistant.render_text(
            image,
            text=battery_capacity_text,
            xy=(3 / 4 * self.size[0], 1 / 2 * self.size[1]),
            font_size=20,
        )
