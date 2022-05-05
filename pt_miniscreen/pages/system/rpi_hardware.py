from functools import partial
from pathlib import Path

import psutil
from pitop.common.formatting import bytes2human

from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText


def rpi_model():
    filename = "/proc/device-tree/model"
    lines = []
    if Path(filename).exists():
        with open(filename) as file:
            lines = [line.strip() for line in file]
    return ", ".join(lines)


def rpi_ram():
    try:
        return f"{bytes2human(psutil.virtual_memory().total)}"
    except Exception:
        return ""


def rpi_serial():
    cpuserial = ""
    filename = "/proc/cpuinfo"
    if Path(filename).exists():
        with open(filename) as file:
            for line in file:
                if line.startswith("Serial"):
                    cpuserial = line.split(":")[1].strip()
    return cpuserial


class HardwarePageInfo:
    def __init__(self):
        self.rpi_model = f"Model: {rpi_model()}"
        self.rpi_ram = f"RAM: {rpi_ram()}"
        self.rpi_serial = f"Serial: {rpi_serial()}"


class RPiHardwarePage(InfoPage):
    def __init__(self, **kwargs):
        info = HardwarePageInfo()
        Row = partial(MarqueeText, font_size=10, vertical_align="center")

        super().__init__(
            **kwargs,
            title="Raspberry Pi",
            Rows=[
                partial(Row, text=info.rpi_model),
                partial(Row, text=info.rpi_ram),
                partial(Row, text=info.rpi_serial),
            ],
        )
