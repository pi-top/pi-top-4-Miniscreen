from datetime import datetime

import psutil

from .templates.text import Hotspot as TextHotspot


class Hotspot(TextHotspot):
    def __init__(
        self,
        size,
        interface,
        interval=1,
    ):
        super().__init__(
            size,
            text="",
            interval=interval,
        )
        self.interface = interface

    @property
    def text(self):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        elapsed = datetime.now() - boot_time
        time = "{0} s".format(int(elapsed.total_seconds()))

        return f"Uptime: {time}"

    @text.setter
    def text(self, value_or_callback):
        # Nothing to do
        pass
