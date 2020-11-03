from ptoled import get_device_instance
from components.Page import MenuPage
from components.widgets.sys_info import (
    batt_level,
    uptime,
    memory,
    disk,
    cpu_load,
    clock,
    wifi,
    network,
    usb,
    date_time,
    ethernet
)
from components.widgets.main import template as main_menu_page
from components.widgets.settings import (
    template as settings_menu_page,
    settings as setting_title,
)
from components.widgets.projects import template as projects_menu_page
from components.widgets.first_time_setup import first_time_setup
from components.widgets.error import template as error_page
from pitop.core.logger import PTLogger
from pitop.core.sys_info import (
    get_ssh_enabled_state,
    get_vnc_enabled_state,
    get_systemd_enabled_state,
    get_pt_further_link_enabled_state,
    is_pi,
    get_battery_capacity,
    get_battery_charging_state,
)

from luma.core.virtual import viewport
from enum import Enum
from os import path, listdir, kill, system
from pathlib import Path
import signal
from subprocess import check_output, Popen

_app = None

# Used by SubscriberClient to pass the battery info to the battery page
try:
    battery_charging_state = get_battery_charging_state()
except:
    battery_charging_state = None

try:
    battery_capacity = get_battery_capacity()
except:
    battery_capacity = None


def get_battery_charging_state():
    return battery_charging_state


def get_battery_capacity():
    return battery_capacity


def set_app(top_level_app_obj):
    global _app
    _app = top_level_app_obj


def change_menu(menu_id):
    def run():
        _app.change_menu(menu_id)

    return run


def enable_and_start_systemd_service(service_to_enable):
    system("sudo systemctl enable " + service_to_enable)
    system("sudo systemctl start " + service_to_enable)


def disable_and_stop_systemd_service(service_to_disable):
    system("sudo systemctl disable " + service_to_disable)
    system("sudo systemctl stop " + service_to_disable)


def change_service_enabled_state(service):
    state = get_systemd_enabled_state(service)

    if state == "Enabled":
        disable_and_stop_systemd_service(service)
    elif state == "Disabled":
        enable_and_start_systemd_service(service)


def change_ssh_enabled_state():
    change_service_enabled_state("ssh")


def change_vnc_enabled_state():
    change_service_enabled_state("vncserver-x11-serviced.service")


def change_pt_further_link_enabled_state():
    change_service_enabled_state("pt-further-link.service")


def reset_hdmi_configuration():
    # Close 'Screen Layout Editor'
    system("DISPLAY=:0 wmctrl -c \"Screen Layout Editor\"")

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
                    "Project already running: "
                    + str(path_to_project)
                    + ". Attempting to stop..."
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


def get_hotspot(widget, interval=0.0, **extra_data):
    data = {
        **{"width": get_device_instance().width, "height": get_device_instance().height, "interval": interval},
        **extra_data,
    }
    return widget.Hotspot(**data)


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4
    FIRST_TIME = 5


class Pages:
    class SysInfoMenu(Enum):
        BATTERY = MenuPage(
            name="battery",
            hotspot=get_hotspot(
                batt_level,
                interval=1.0,
                battery_charging_state=get_battery_charging_state,
                battery_capacity=get_battery_capacity,
            ),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )
        # UPTIME = MenuPage(
        #     name="uptime",
        #     hotspot=get_hotspot(uptime, interval=1.0),
        #     select_action_func=change_menu(Menus.MAIN_MENU),
        #     cancel_action_func=None,
        # )
        # MEMORY = MenuPage(
        #     name="memory",
        #     hotspot=get_hotspot(memory, interval=2.0),
        #     select_action_func=change_menu(Menus.MAIN_MENU),
        #     cancel_action_func=None,
        # )
        # DISK = MenuPage(
        #     name="disk",
        #     hotspot=get_hotspot(disk, interval=2.0),
        #     select_action_func=change_menu(Menus.MAIN_MENU),
        #     cancel_action_func=None,
        # )
        CPU = MenuPage(
            name="cpu",
            hotspot=get_hotspot(cpu_load, interval=0.5),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )
        # CLOCK = MenuPage(
        #     name="clock",
        #     hotspot=get_hotspot(clock, interval=1.0),
        #     select_action_func=change_menu(Menus.MAIN_MENU),
        #     cancel_action_func=None,
        # )
        WIFI = MenuPage(
            name="wifi",
            hotspot=get_hotspot(wifi, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )
        # NETWORK = MenuPage(
        #     name="network",
        #     hotspot=get_hotspot(network, interval=1.0, interface="wlan0"),
        #     select_action_func=change_menu(Menus.MAIN_MENU),
        #     cancel_action_func=None,
        # )

        USB_SETUP = MenuPage(
            name="usb",
            hotspot=get_hotspot(usb, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )
        ETHERNET_PAGE = MenuPage(
            name="ethernet",
            hotspot=get_hotspot(ethernet, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )
        DATE_TIME = MenuPage(
            name="date_time",
            hotspot=get_hotspot(date_time, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None,
        )

    class MainMenu(Enum):
        SETTINGS_SELECT = MenuPage(
            name="Settings",
            hotspot=get_hotspot(setting_title, title="Settings", interval=1.0),
            select_action_func=change_menu(Menus.SETTINGS),
            cancel_action_func=None,
        )

        # WIFI_SETUP_SELECT = MenuPage(
        #     name="Wi-Fi Setup",
        #     hotspot=get_hotspot(main_menu,
        #                         title="Wi-Fi Setup"),
        #     select_action_func=None,  # change_menu(Menus.WIFI_SETUP)
        #     cancel_action_func=None
        # )
        # # Alexa/Mycroft?
        # VOICE_ASSISTANT_SELECT = MenuPage(
        #     name="Voice Assistant",
        #     hotspot=get_hotspot(main_menu,
        #                         title="Voice Assistant"),
        #     select_action_func=None,  # change_menu(Menus.VOICE_ASSIST)
        #     cancel_action_func=None
        # )

    class SettingsMenu(Enum):
        SSH_CONNECTION = MenuPage(
            name="ssh_connection",
            hotspot=get_hotspot(
                settings_menu_page,
                type="ssh",
                interval=1.0,
                get_state_method=get_ssh_enabled_state,
            ),
            select_action_func=change_ssh_enabled_state,
            cancel_action_func=change_menu(Menus.MAIN_MENU),
        )
        VNC_CONNECTION = MenuPage(
            name="vnc_connection",
            hotspot=get_hotspot(
                settings_menu_page,
                type="vnc",
                interval=1.0,
                get_state_method=get_vnc_enabled_state,
            ),
            select_action_func=change_vnc_enabled_state,
            cancel_action_func=change_menu(Menus.MAIN_MENU),
        )
        PT_FURTHER_LINK_CONNECTION = MenuPage(
            name="pt_further_link",
            hotspot=get_hotspot(
                settings_menu_page,
                type="pt_further_link",
                interval=1.0,
                get_state_method=get_pt_further_link_enabled_state,
            ),
            select_action_func=change_pt_further_link_enabled_state,
            cancel_action_func=change_menu(Menus.MAIN_MENU),
        )
        DISPLAY_RESET = MenuPage(
            name="hdmi_reset",
            hotspot=get_hotspot(
                settings_menu_page,
                type="hdmi_reset",
                interval=0.0,
                get_state_method=None,
            ),
            select_action_func=reset_hdmi_configuration,
            cancel_action_func=change_menu(Menus.MAIN_MENU),
        )

    class ProjectSelectMenu:
        @staticmethod
        def generate_pages():
            project_dir = path.expanduser("~/Desktop/My Projects")
            project_pages = list()
            if path.exists(project_dir):
                # For each directory in project path
                project_subdirs = [
                    name
                    for name in sorted(listdir(project_dir))
                    if path.isdir(path.join(project_dir, name))
                ]
                for project_subdir in project_subdirs:
                    # Get name from path
                    title = project_subdir
                    project_path = project_dir + "/" + project_subdir

                    project_page = MenuPage(
                        title,
                        get_hotspot(
                            projects_menu_page, title=title, project_path=project_path
                        ),
                        start_stop_project(project_path),
                        None,
                    )
                    project_pages.append(project_page)
                if not project_pages:
                    title = "No Projects Found"

                    project_page = MenuPage(
                        title,
                        get_hotspot(main_menu_page, title=title,
                                    image_path=None),
                        None,
                        None,
                    )
                    project_pages.append(project_page)
            else:
                title = "Project Directory"
                second_line = "Not Found"

                project_page = MenuPage(
                    title,
                    get_hotspot(
                        error_page,
                        title=title,
                        second_line=second_line,
                        image_path=None,
                    ),
                    None,
                    None,
                )
                project_pages.append(project_page)
            return project_pages

    class FirstTimeSetupMenu(Enum):
        INTRO = MenuPage(
            name="initial_setup",
            hotspot=get_hotspot(first_time_setup, interval=1),
            select_action_func=None,
            cancel_action_func=None,
        )


def get_menu_enum_class_from_name(menu_name):
    if menu_name == Menus.SYS_INFO:
        return Pages.SysInfoMenu
    elif menu_name == Menus.MAIN_MENU:
        return Pages.MainMenu
    elif menu_name == Menus.PROJECTS:
        return Pages.ProjectSelectMenu
    elif menu_name == Menus.SETTINGS:
        return Pages.SettingsMenu
    elif menu_name == Menus.FIRST_TIME:
        return Pages.FirstTimeSetupMenu
    else:
        _app.stop()
        raise Exception("Unrecognised menu name: " + menu_name.name)


def get_pages(menu_name):
    pages_enum = get_menu_enum_class_from_name(menu_name)

    if hasattr(pages_enum, "__members__"):
        return [
            page_name.value for page_id, page_name in pages_enum.__members__.items()
        ]
    else:
        return pages_enum.generate_pages()


def get_page_ids(menu_name):
    pages_enum = get_menu_enum_class_from_name(menu_name)
    return pages_enum.__members__.items()


def get_enum_key_from_value(menu_name, value):
    pages_enum = get_menu_enum_class_from_name(menu_name)
    for page_id, page_enum in pages_enum.__members__.items():
        page = page_enum.value
        if page.name == value:
            return pages_enum[page_id].value
    _app.stop()
    raise Exception("Unable to find enum key matching value: " + value)


def create_viewport(device, pages):
    viewport_height = sum(page.hotspot.height for page in pages)
    virtual = viewport(device, width=device.width, height=viewport_height)

    # Start at second page, so that last entry can be added to the start for scrolling
    created_viewport_height = 0
    for i, page in enumerate(pages):
        virtual.add_hotspot(page.hotspot, (0, created_viewport_height))
        created_viewport_height += page.hotspot.height

    return virtual


def remove_invalid_sys_info_widget_names(widget_name_list):
    for widget_name in widget_name_list:
        if widget_name not in (page.name for page in get_pages(Menus.SYS_INFO)):
            PTLogger.debug(
                "Removing invalid sys info widget: " + str(widget_name))
            widget_name_list.remove(widget_name)
    return widget_name_list


def get_sys_info_pages():
    page_name_arr = ["battery", "cpu", "wifi", "ethernet", "usb"]

    page_id_arr = list()
    for page_name in page_name_arr:
        page_id = get_enum_key_from_value(Menus.SYS_INFO, page_name)
        page_id_arr.append(page_id)

    return page_id_arr
