from pitop.common.sys_info import get_ap_mode_status

from pt_miniscreen.widgets.common import BaseNetworkingSysInfoSnapshot


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "ap"
        self.human_readable_name = "Access Point"

        super(Hotspot, self).__init__(
            name=self.name,
            human_readable_name=self.human_readable_name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render,
        )

    def set_data_members(self):
        ap_data = get_ap_mode_status()
        self.first_line = ap_data.get("ssid", "")
        self.second_line = ap_data.get("passphrase", "")
        self.third_line = ap_data.get("ip_address", "")
