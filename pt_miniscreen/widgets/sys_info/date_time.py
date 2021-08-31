import datetime
from pt_miniscreen.widgets.common import BaseSnapshot, title_text, draw_text, align_to_middle, common_first_line_y, common_second_line_y


class Hotspot(BaseSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        date_time = datetime.datetime.now()
        date = f"{date_time.day}/{date_time.month}/{date_time.year}"
        time = f"{date_time.hour}:{date_time.minute}:{date_time.second}"

        title_text(draw, common_first_line_y, width, date)

        draw_text(
            draw,
            xy=(align_to_middle(draw, width, time), common_second_line_y),
            text=time,
        )
