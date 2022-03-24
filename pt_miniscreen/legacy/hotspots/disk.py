import psutil
from pitop.common.formatting import bytes2human

from .templates.text import Hotspot as Text


class Hotspot(Text):
    def __init__(
        self,
        size,
        text,
        interval=5,
    ):
        super().__init__(
            size,
            text,
            interval=interval,
        )

    @property
    def text(self):
        df = psutil.disk_usage("/")

        return f"""Disk
        Used: {"{0:0.1f}%".format(df.percent)}
        Free: {bytes2human(df.free, "{0:0.0f}")}
        Total: {bytes2human(df.total, "{0:0.0f}")}
        """

    @text.setter
    def text(self, value_or_callback):
        # Nothing to do
        pass
