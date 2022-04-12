from pathlib import Path

import psutil
from pitop.common.formatting import bytes2human

from ..network.network_page_base import NetworkPageData
from ..network.network_page_base import Page as PageBase
from ..network.network_page_base import RowDataText


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


class Page(PageBase):
    def __init__(self, size):
        info = HardwarePageInfo()
        row_data = NetworkPageData(
            first_row=RowDataText(text=lambda: info.rpi_model),
            second_row=RowDataText(text=lambda: info.rpi_ram),
            third_row=RowDataText(text=lambda: info.rpi_serial),
        )
        super().__init__(size=size, row_data=row_data, title="Raspberry Pi")
