from isc_dhcp_leases import IscDhcpLeases


def interface_is_up(interface_name):
    contents = ""
    with open("/sys/class/net/" + interface_name + "/operstate", "r") as file:
        contents = file.read()

    return "up" in contents


def get_address_for_ptusb_connected_device():
    if interface_is_up("ptusb0"):
        current_leases_dict = IscDhcpLeases(
            '/var/lib/dhcp/dhcpd.leases').get_current()
        for lease in current_leases_dict.values():
            return lease.ip

    return ""
