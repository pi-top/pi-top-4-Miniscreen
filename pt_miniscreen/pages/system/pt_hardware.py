from pathlib import Path
from threading import Thread

from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.firmware_device import FirmwareDevice

from ..network.network_page_base import NetworkPageData
from ..network.network_page_base import Page as PageBase
from ..network.network_page_base import RowDataText


def get_pt_serial():
    filename = "/var/run/pt_hub_serial"
    lines = []
    if Path(filename).exists():
        with open(filename) as file:
            lines = [line.strip() for line in file]
    return ", ".join(lines)


class HardwarePageInfo:
    def __init__(self):
        self._fw_version = "Unknown"
        self._hw_version = "Unknown"

        self.pt_serial = f"Serial: {get_pt_serial()}"

        def update_params():
            try:
                device = FirmwareDevice(FirmwareDeviceID.pt4_hub, 0.1)
                self._fw_version = device.get_fw_version()
                self._hw_version = device.get_sch_hardware_version_major()
            except Exception:
                pass

        thread = Thread(target=update_params, args=(), daemon=True)
        thread.start()

    @property
    def fw_version(self):
        return f"Firmware: {self._fw_version}"

    @property
    def hw_version(self):
        return f"Hardware: {self._hw_version}"


class Page(PageBase):
    def __init__(self, size):
        info = HardwarePageInfo()
        row_data = NetworkPageData(
            first_row=RowDataText(text=lambda: info.fw_version),
            second_row=RowDataText(text=lambda: info.hw_version),
            third_row=RowDataText(text=lambda: info.pt_serial),
        )
        super().__init__(size=size, row_data=row_data, title="pi-top Hardware")
