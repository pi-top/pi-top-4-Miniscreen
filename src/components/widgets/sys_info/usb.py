from components.widgets.common.base_widgets import BaseNetworkingSysInfoSnapshot

from pitop.common.pt_os import is_pi_using_default_password
from pitop.common.sys_info import (
    get_internal_ip,
    get_address_for_ptusb_connected_device
)

from ctypes import c_bool
from getpass import getuser
from ipaddress import ip_address
from multiprocessing import (
    Process,
    Value,
)
from time import sleep


class Hotspot(BaseNetworkingSysInfoSnapshot):
    def __init__(self, width, height, mode, interval, **data):
        self.name = "usb"
        self.human_readable_name = "USB"

        super(Hotspot, self).__init__(
            name=self.name,
            human_readable_name=self.human_readable_name,
            width=width,
            height=height,
            mode=mode,
            interval=interval,
            draw_fn=self.render
        )

        self._is_connected = Value(c_bool, False)

        self.connection_status_thread = Process(
            target=self.__update_connection_status)
        self.connection_status_thread.daemon = True
        self.connection_status_thread.start()

    def __update_connection_status(self):
        while True:
            self._is_connected.value = (get_address_for_ptusb_connected_device() != "")
            sleep(0.3)

    def is_connected(self):
        return self._is_connected.value

    def set_data_members(self):
        self.first_line = "pi" if getuser() == "root" else getuser()
        self.second_line = "pi-top" if is_pi_using_default_password() is True else "********"
        try:
            self.third_line = ip_address(get_internal_ip(iface="ptusb0"))
        except ValueError:
            self.third_line = ""
