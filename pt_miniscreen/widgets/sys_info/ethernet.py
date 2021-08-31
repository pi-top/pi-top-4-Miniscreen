from ipaddress import ip_address

from pitop.common.sys_info import get_internal_ip

from pt_miniscreen.widgets.common import BaseNetworkingSysInfoSnapshot


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "ethernet"
        self.human_readable_name = "LAN"

        super(Hotspot, self).__init__(
            name=self.name,
            human_readable_name=self.human_readable_name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render,
        )

    def is_connected(self):
        return self.second_line != ""

    def set_data_members(self):
        try:
            internal_eth0_ip = get_internal_ip(iface="eth0")
            parsed_ip = ip_address(internal_eth0_ip)
            self.second_line = parsed_ip
        except ValueError:
            self.second_line = ""
