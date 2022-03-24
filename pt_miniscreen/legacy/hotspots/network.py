from typing import List

import psutil
from pitop.common.formatting import bytes2human

from .templates.text import Hotspot as Text


class Hotspot(Text):
    def __init__(
        self,
        size,
        interface,
        interval=2,
    ):
        super().__init__(
            size,
            text="",
            interval=interval,
        )
        self.interface = interface

    @property
    def text(self):
        title_line = f"Net: {self.interface}"
        data_lines: List[str] = list()
        try:
            address = psutil.net_if_addrs()[self.interface][0].address
            counters = psutil.net_io_counters(pernic=True)[self.interface]

            data_lines.append(address)
            data_lines.append(f"Rx: {bytes2human(counters.bytes_recv)}")
            data_lines.append(f"Tx: {bytes2human(counters.bytes_sent)}")
        except Exception:
            data_lines.append("N/A")

        return title_line + "\n" + data_lines.join("'n")

    @text.setter
    def text(self, value_or_callback):
        # Nothing to do
        pass
