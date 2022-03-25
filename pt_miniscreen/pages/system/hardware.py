from dataclasses import dataclass
from pathlib import Path

import psutil
from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.formatting import bytes2human
from pt_fw_updater.update import create_firmware_device

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.marquee_dynamic_text import (
    Hotspot as MarqueeDynamicTextHotspot,
)
from ..base import Page as PageBase


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


@dataclass
class HardwarePageInfo:
    fw_version: str = f"Firmware Version: {get_fw_version()}"
    hw_version: str = f"Hardware Version: {get_hw_version()}"
    pt_serial: str = f"pi-top Serial Number: {get_pt_serial()}"
    rpi_model: str = f"Raspberry Pi Model: {rpi_model()}"
    rpi_ram: str = f"Raspberry Pi RAM: {rpi_ram()}"
    rpi_serial: str = f"Raspberry Pi Serial Number: {rpi_serial()}"


X_MARGIN = 5
ROW_HEIGHT = 10
TEXT_FONT_SIZE = 10
MARGIN_Y = 5


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)
        self.info = HardwarePageInfo()
        self.reset()

    def reset(self):

        self.hotspot_instances = [
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.fw_version,
                ),
                (X_MARGIN, MARGIN_Y),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.hw_version,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.pt_serial,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT * 2),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.rpi_model,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT * 3),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.rpi_ram,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT * 4),
            ),
            HotspotInstance(
                MarqueeDynamicTextHotspot(
                    size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                    font_size=TEXT_FONT_SIZE,
                    text=lambda: self.info.rpi_serial,
                ),
                (X_MARGIN, MARGIN_Y + ROW_HEIGHT * 5),
            ),
        ]
