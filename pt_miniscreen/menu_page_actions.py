import signal
from os import kill, path, system
from subprocess import Popen, check_output

from pitop.common.command_runner import run_command
from pitop.common.logger import PTLogger
from pitop.common.sys_info import get_ap_mode_status, get_systemd_enabled_state


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


def change_further_link_enabled_state():
    __change_service_enabled_state("pt-further-link.service")


def change_wifi_mode():
    if get_wifi_ap_state() == "Enabled":
        run_command("/usr/bin/wifi-ap-sta stop", timeout=30)
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

        PTLogger.debug("Checking if process is already running...")

        cmd = 'pgrep -f "' + path_to_project + '" || true'
        output = check_output(cmd, shell=True).decode("ascii", "ignore")
        pids = list(filter(None, output.split("\n")))

        try:
            if len(pids) > 1:
                PTLogger.info(
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
                PTLogger.info("Starting project: " + str(path_to_project))

                if path.exists(start_script):
                    PTLogger.debug(
                        "Code file found at " + start_script + ". Running..."
                    )
                    Popen([start_script])
                else:
                    PTLogger.info("No code file found at " + start_script)

        except Exception as e:
            PTLogger.warning("Error starting/stopping process: " + str(e))

    return run
