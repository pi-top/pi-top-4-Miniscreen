from datetime import datetime
from functools import partial
from pathlib import Path
from pitop.common.command_runner import run_command
from pitop.common.firmware_device import FirmwareDevice
from pitop.common.common_names import FirmwareDeviceName
from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.sys_info import get_pi_top_ip
from pt_fw_updater.utils import (
    default_firmware_folder,
    find_latest_firmware,
    is_valid_fw_object,
)
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText


def get_ip_url():
    url = "pi-top.local"
    ip_address = get_pi_top_ip()
    if len(ip_address) > 0:
        url = ip_address
    return f"http://{url}"


def _get_last_update_breadcrumb_mtime():
    filename = "/var/lib/pt-miniscreen/last-update"
    try:
        # Find last modified date from breadcrumb
        mtime = Path(filename).stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def latest_update_date():
    date = _get_last_update_breadcrumb_mtime()
    if date:
        return f"Last update: {date}"
    return "Can't determine last update date"


def system_updates_available():
    updates_available = False
    try:
        output = run_command("apt list --upgradable", timeout=10)
        updates_available = len(output.strip().split("\n")) - 1 > 0
    except Exception:
        updates_available = False
    if updates_available:
        return f"System updates available! Go to {get_ip_url()}/updater"
    return "No system updates available"


def _has_fw_updates():
    for device_enum in FirmwareDeviceName:
        device_str = device_enum.name
        path_to_fw_folder = default_firmware_folder(device_str)
        try:
            fw_device = FirmwareDevice(FirmwareDeviceID[device_str])
            fw_file_object = find_latest_firmware(path_to_fw_folder, fw_device)
            fw_device._i2c_device.disconnect()
            if is_valid_fw_object(fw_file_object):
                return True
        except Exception:
            # Plate not connected
            pass
    return False


def firmware_updates_available():
    if _has_fw_updates():
        return f"Firmware Update available! Go to {get_ip_url()}/vnc"
    return "Firmware is up to date"


class LastUpdatePage(InfoPage):
    def __init__(self, **kwargs):
        Row = partial(MarqueeText, font_size=10, vertical_align="center")

        super().__init__(
            **kwargs,
            title="System Updates",
            Rows=[
                partial(Row, text="", get_text=latest_update_date),
                partial(Row, text="Loading...", get_text=system_updates_available),
                partial(Row, text="", get_text=firmware_updates_available),
            ],
        )
