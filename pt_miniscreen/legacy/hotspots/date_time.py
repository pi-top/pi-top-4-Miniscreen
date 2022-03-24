import datetime

from .templates.text import Hotspot as Text


class Hotspot(Text):
    def __init__(
        self,
        size,
        text,
        interval=1,
    ):
        super().__init__(
            size,
            text,
            interval=interval,
        )

    @property
    def text(self):
        date_time = datetime.datetime.now()
        date = f"{date_time.day}/{date_time.month}/{date_time.year}"
        time = f"{date_time.hour}:{date_time.minute}:{date_time.second}"
        return f"{date} {time}"

    @text.setter
    def text(self, value_or_callback):
        # Nothing to do
        pass
