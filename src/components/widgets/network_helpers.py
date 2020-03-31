from isc_dhcp_leases import IscDhcpLeases
from ptcommon.logger import PTLogger
from ptcommon.command_runner import run_command


def interface_is_up(interface_name):
    contents = ""
    with open("/sys/class/net/" + interface_name + "/operstate", "r") as file:
        contents = file.read()

    return "up" in contents


def get_address_for_ptusb_connected_device():
    if interface_is_up("ptusb0"):
        for lease in IscDhcpLeases(
                '/var/lib/dhcp/dhcpd.leases').get_current().values():
            try:
                PTLogger.debug(
                    "Checking if leased IP address {} is connected.".format(lease.ip))
                run_command("ping -c1 {}".format(lease.ip),
                            timeout=0.1, check=True)
                PTLogger.debug(
                    "Leased IP address {} is connected.".format(lease.ip))
                return lease.ip
            except Exception as e:
                PTLogger.debug(
                    "Leased IP address {} is not connected.".format(lease.ip))
                continue
    return ""
