import os

# pt-os-update-monitor writes this while it holds off a shutdown for an update
UPDATE_HOLD_FILE = "/run/systemd/system/poweroff.target.d/reboot-guard.conf"


def is_updating() -> bool:
    return os.path.exists(UPDATE_HOLD_FILE)
