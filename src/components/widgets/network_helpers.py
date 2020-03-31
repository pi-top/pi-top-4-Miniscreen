from isc_dhcp_leases import IscDhcpLeases
from ptcommon.logger import PTLogger
from ptcommon.command_runner import run_command


def interface_is_up(interface_name):
    contents = ""
    with open("/sys/class/net/" + interface_name + "/operstate", "r") as file:
        contents = file.read()

    return "up" in contents


def get_address_for_ptusb_connected_device():
    if not interface_is_up("ptusb0"):
        return ""

    current_leases_dict = IscDhcpLeases(
        '/var/lib/dhcp/dhcpd.leases').get_current()
    for lease in current_leases_dict.values():
        try:
            PTLogger.info(
                "Checking if leased ip {} is connected.".format(lease.ip))
            run_command("ping -c1 {}".format(lease.ip),
                        timeout=0.1, check=True)
            PTLogger.info("IP {} is connected.".format(lease.ip))
            return lease.ip
        except Exception as e:
            PTLogger.info("{} is not connected.".format(lease.ip))
            continue
    return ""
