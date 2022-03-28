from dataclasses import dataclass
from pathlib import Path

from pitop.common.common_ids import FirmwareDeviceID
from pt_fw_updater.update import create_firmware_device

from ..network.network_page_base import NetworkPageData
from ..network.network_page_base import Page as PageBase
from ..network.network_page_base import RowDataText


def get_fw_version():
    try:
        device = create_firmware_device(FirmwareDeviceID.pt4_hub, 1)
        return device.get_fw_version()
    except Exception:
        return ""


def get_hw_version():
    try:
        device = create_firmware_device(FirmwareDeviceID.pt4_hub, 1)
        return device.get_sch_hardware_version_major()
    except Exception:
        return ""


def get_pt_serial():
    filename = "/var/run/pt_hub_serial"
    lines = []
    if Path(filename).exists():
        with open(filename) as file:
            lines = [line.strip() for line in file]
    return ", ".join(lines)


@dataclass
class HardwarePageInfo:
    fw_version: str = f"Firmware Version: {get_fw_version()}"
    hw_version: str = f"Hardware Version: {get_hw_version()}"
    pt_serial: str = f"pi-top Serial Number: {get_pt_serial()}"


info = HardwarePageInfo()


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            first_row=RowDataText(text=lambda: info.fw_version),
            second_row=RowDataText(text=lambda: info.hw_version),
            third_row=RowDataText(text=lambda: info.pt_serial),
        )
        super().__init__(size=size, row_data=row_data, title="pi-top Hardware")
