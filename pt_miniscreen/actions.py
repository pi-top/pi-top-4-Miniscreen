import logging
import signal
from os import kill, path, system
from subprocess import Popen, check_output

from pitop.common.command_runner import run_command
from pitop.common.configuration_file import add_section, has_section, remove_section
from pitop.common.sys_info import get_ap_mode_status, get_systemd_enabled_state

logger = logging.getLogger(__name__)

CUSTOM_PREPEND_DNS_RESOLVER_CONFIG_FILE = "/etc/resolv.conf.head"


def __enable_and_start_systemd_service(service_to_enable):
    system("sudo systemctl enable " + service_to_enable)
    system("sudo systemctl start " + service_to_enable)


def __disable_and_stop_systemd_service(service_to_disable):
    system("sudo systemctl disable " + service_to_disable)
    system("sudo systemctl stop " + service_to_disable)


def __change_service_enabled_state(service):
    state = get_systemd_enabled_state(service)

    if state == "Enabled":
        __disable_and_stop_systemd_service(service)
    elif state == "Disabled":
        __enable_and_start_systemd_service(service)


def change_ssh_enabled_state():
    __change_service_enabled_state("ssh")


def change_vnc_enabled_state():
    __change_service_enabled_state("vncserver-x11-serviced.service")

    # Force vncserver-x11-serviced and pt-web-vnc-desktop services status to match
    vncserver_state = get_systemd_enabled_state("vncserver-x11-serviced.service")
    pt_web_vnc_state = get_systemd_enabled_state("pt-web-vnc-desktop.service")
    if vncserver_state != pt_web_vnc_state:
        __change_service_enabled_state("pt-web-vnc-desktop.service")


def change_further_link_enabled_state():
    __change_service_enabled_state("further-link.service")


def change_wifi_mode():
    if get_wifi_ap_state() == "Enabled":
        run_command("/usr/bin/wifi-ap-sta stop", timeout=30)
        run_command("/usr/bin/wifi-ap-sta disable", timeout=30)
    else:
        run_command("/usr/bin/wifi-ap-sta start", timeout=30)


def get_wifi_ap_state():
    status_data = get_ap_mode_status()
    if status_data.get("state", "").lower() == "active":
        return "Enabled"
    return "Disabled"


def reset_hdmi_configuration():
    # Close 'Screen Layout Editor'
    system('DISPLAY=:0 wmctrl -c "Screen Layout Editor"')

    # Reset all HDMI outputs to lowest common resolution
    system("DISPLAY=:0 autorandr -c common")

    # Show 'Screen Layout Editor'
    # system("DISPLAY=:0 arandr &")

    # Reset DPMS - show display if they were blanked
    system("DISPLAY=:0 xset dpms force on")


def start_stop_project(path_to_project):
    def run():
        start_script = path_to_project + "/start.sh"
        stop_script = path_to_project + "/stop.sh"

        logger.debug("Checking if process is already running...")

        cmd = 'pgrep -f "' + path_to_project + '" || true'
        output = check_output(cmd, shell=True).decode("ascii", "ignore")
        pids = list(filter(None, output.split("\n")))

        try:
            if len(pids) > 1:
                logger.info(
                    f"Project already running: {path_to_project}. Attempting to stop..."
                )

                if path.exists(stop_script):
                    Popen([stop_script])
                else:
                    for pid in pids:
                        try:
                            kill(int(pid), signal.SIGTERM)
                        except ValueError:
                            pass
            else:
                logger.info("Starting project: " + str(path_to_project))

                if path.exists(start_script):
                    logger.debug("Code file found at " + start_script + ". Running...")
                    Popen([start_script])
                else:
                    logger.info("No code file found at " + start_script)

        except Exception as e:
            logger.warning("Error starting/stopping process: " + str(e))

    return run


def add_cloudflare_dns():
    if cloudflare_dns_is_set() == "Enabled":
        return

    add_section(
        filename=CUSTOM_PREPEND_DNS_RESOLVER_CONFIG_FILE,
        title="pt-miniscreen-cloudflare-dns",
        description="Add Cloudflare DNS to solve connection issues with Further.",
        content="""nameserver 1.1.1.1
nameserver 1.0.0.1
nameserver 2606:4700:4700::1111
nameserver 2606:4700:4700::1001
""",
    )


def remove_cloudflare_dns():
    remove_section(
        filename=CUSTOM_PREPEND_DNS_RESOLVER_CONFIG_FILE,
        title="pt-miniscreen-cloudflare-dns",
    )


def cloudflare_dns_is_set():
    is_set = has_section(
        filename=CUSTOM_PREPEND_DNS_RESOLVER_CONFIG_FILE,
        title="pt-miniscreen-cloudflare-dns",
    )
    return "Enabled" if is_set else "Disabled"


def update_resolvconf_configuration():
    run_command("resolvconf -u", timeout=5)


def toggle_cloudflare_dns():
    if cloudflare_dns_is_set() == "Enabled":
        remove_cloudflare_dns()
    else:
        add_cloudflare_dns()

    update_resolvconf_configuration()


def get_bluetooth_gatt_encryption_state():
    state = run_command(
        "/usr/bin/further-link-bluetooth-encryption", timeout=10
    ).strip()
    return "Enabled" if state in ("true", "1") else "Disabled"


def toggle_bluetooth_gatt_encryption_state():
    using_encryption = get_bluetooth_gatt_encryption_state() == "Enabled"
    run_command(
        f"sudo /usr/bin/further-link-bluetooth-encryption {'false' if using_encryption else 'true'}",
        timeout=10,
    )
    # restart further-link service to apply changes
    run_command("sudo systemctl restart further-link.service", timeout=10)
