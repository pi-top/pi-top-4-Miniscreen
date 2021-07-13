from components.widgets.common.base_widgets import BaseNetworkingSysInfoSnapshot
from pitopcommon.sys_info import get_internal_ip
from ipaddress import ip_address


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "ethernet"

        super(Hotspot, self).__init__(
            name=self.name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render
        )

    def is_connected(self):
        return self.second_line != ""

    def set_data_members(self):
        try:
            self.second_line = ip_address(get_internal_ip(iface="eth0"))
        except ValueError:
            self.second_line = ""
