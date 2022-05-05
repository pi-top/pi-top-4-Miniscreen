from functools import partial
from pathlib import Path
from threading import Thread

from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.firmware_device import FirmwareDevice

from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText


def get_pt_serial():
    filename = "/var/run/pt_hub_serial"
    lines = []
    if Path(filename).exists():
        with open(filename) as file:
            lines = [line.strip() for line in file]
    return ", ".join(lines)


class PitopHardwarePage(InfoPage):
    firmware = ""
    hardware = ""
    serial = ""

    def __init__(self, **kwargs):
        Row = partial(MarqueeText, font_size=10, vertical_align="center")

        super().__init__(
            **kwargs,
            title="pi-top Hardware",
            Rows=[
                partial(Row, text=PitopHardwarePage.firmware or "Loading..."),
                partial(Row, text=PitopHardwarePage.hardware),
                partial(Row, text=PitopHardwarePage.serial),
            ],
        )

        def update_info():
            try:
                device = FirmwareDevice(FirmwareDeviceID.pt4_hub, 0.1)
                PitopHardwarePage.firmware = f"Firmware: {device.get_fw_version()}"
                PitopHardwarePage.hardware = (
                    f"Hardware: {device.get_sch_hardware_version_major()}"
                )
                PitopHardwarePage.serial = f"Serial: {get_pt_serial()}"

                self.list.rows[0].state.update({"text": PitopHardwarePage.firmware})
                self.list.rows[1].state.update({"text": PitopHardwarePage.hardware})
                self.list.rows[2].state.update({"text": PitopHardwarePage.serial})
            except Exception:
                pass

        Thread(target=update_info, daemon=True).start()
