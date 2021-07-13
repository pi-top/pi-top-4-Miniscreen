from components.widgets.common.base_widgets import BaseNetworkingSysInfoSnapshot
from pitopcommon.sys_info import get_ap_mode_status


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "ap"

        super(Hotspot, self).__init__(
            name=self.name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render
        )

    def set_data_members(self):
        ap_data = get_ap_mode_status()
        self.first_line = ap_data.get("ssid", "")
        self.second_line = ap_data.get("passphrase", "")
        self.third_line = ap_data.get("ip_address", "")
