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


class HardwarePageInfo:
    def __init__(self):
        self.fw_version = f"Firmware {get_fw_version()}"
        self.hw_version = f"Hardware {get_hw_version()}"
        self.pt_serial = f"Serial {get_pt_serial()}"


class Page(PageBase):
    def __init__(self, size):
        info = HardwarePageInfo()
        row_data = NetworkPageData(
            first_row=RowDataText(text=lambda: info.fw_version),
            second_row=RowDataText(text=lambda: info.hw_version),
            third_row=RowDataText(text=lambda: info.pt_serial),
        )
        super().__init__(size=size, row_data=row_data, title="pi-top Hardware")
