from pt_miniscreen.actions import (
    toggle_bluetooth_gatt_encryption_state,
    get_bluetooth_gatt_encryption_state,
)
from pt_miniscreen.components.action_page import ActionPage


class BluetoothEncryptedGattTogglePage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Bluetooth Encrypted GATT",
            font_size=9,
            action=toggle_bluetooth_gatt_encryption_state,
            get_enabled_state=get_bluetooth_gatt_encryption_state,
            **kwargs,
        )
