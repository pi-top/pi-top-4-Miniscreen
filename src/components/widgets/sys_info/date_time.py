import datetime
from components.widgets.common.common_functions import title_text, draw_text, align_to_middle
from components.widgets.common.common_values import common_first_line_y, common_second_line_y
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        date_time = datetime.datetime.now()
        date = (
            str(date_time.day) + "/" + str(date_time.month) +
            "/" + str(date_time.year)
        )
        time = (
            str(date_time.hour)
            + ":"
            + str(date_time.minute)
            + ":"
            + str(date_time.second)
        )

        title_text(draw, common_first_line_y, width, date)

        draw_text(
            draw,
            xy=(align_to_middle(draw, width, time), common_second_line_y),
            text=time,
        )
