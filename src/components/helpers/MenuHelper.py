from components.System import device, is_pi
from components.Page import MenuPage
from components.widgets.common import image
from components.widgets.sys_info import (
    batt_level,
    uptime,
    memory,
    disk,
    cpu_load,
    clock,
    hud,
    wifi,
    network
)
from components.widgets.main import template as main_menu
from components.widgets.projects import template as projects_menu
from ptcommon.logger import PTLogger

from luma.core.virtual import viewport
from enum import Enum
from os import (
    path,
    listdir
)
from pathlib import Path
from subprocess import (
    check_output,
    Popen
)
from psutil import Process

_app = None


def set_app(top_level_app_obj):
    global _app
    _app = top_level_app_obj


def change_menu(menu_id):
    def run():
        _app.change_menu(menu_id)
    return run


def start_stop_project(path_to_project):
    def run():
        PTLogger.info("Attempting to start/stop project: " + str(path_to_project))

        code_file = path_to_project + "/remote_rpi/run.py"

        PTLogger.debug("Checking if process is already running...")
        pid = None

        cmd = "pgrep -f \"" + code_file + "\" || true"
        output = check_output(cmd, shell=True).decode('ascii', 'ignore')
        try:
            pid = int(output)
        except ValueError:
            pass  # No process found - don't worry about it

        if pid is not None:
            PTLogger.debug("Process is running - attempting to kill")
            Process(pid).terminate()
        else:
            PTLogger.debug("Process is not running")
            if path.exists(code_file):
                PTLogger.debug("Code file found at " + code_file + ". Running...")
                Popen(["python3", code_file])
            else:
                PTLogger.debug("No code file found at " + code_file)
    return run


def get_hotspot(widget, interval=0.0, **extra_data):
    data = {
        **{
            "width": device.width,
            "height": device.height,
            "interval": interval
        },
        **extra_data
    }
    return widget.Hotspot(**data)


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4


class Pages:
    class SysInfoMenu(Enum):
        DEMO_STARTUP_SCREEN = MenuPage(
            name="demo_startup",
            hotspot=get_hotspot(
                image,
                image_path=path.abspath(
                    path.join(path.dirname(__file__), '..', '..', 'demo', 'startup.gif')),
                loop=True
            ),
            # on_finished_func=change_menu(Menus.MAIN_MENU),
            select_action_func=None,
            cancel_action_func=None
        )

        DEMO_HUD = MenuPage(
            name="demo_hud",
            hotspot=get_hotspot(
                image,
                image_path=path.abspath(
                    path.join(path.dirname(__file__), '..', '..', 'demo', 'mainmenu-hud.gif')),
            ),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )

        BATTERY = MenuPage(
            name="battery",
            hotspot=get_hotspot(batt_level, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        UPTIME = MenuPage(
            name="uptime",
            hotspot=get_hotspot(uptime, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        MEMORY = MenuPage(
            name="memory",
            hotspot=get_hotspot(memory, interval=2.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        DISK = MenuPage(
            name="disk",
            hotspot=get_hotspot(disk, interval=2.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        CPU = MenuPage(
            name="cpu",
            hotspot=get_hotspot(cpu_load, interval=0.5),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        CLOCK = MenuPage(
            name="clock",
            hotspot=get_hotspot(clock, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        HUD = MenuPage(
            name="hud",
            hotspot=get_hotspot(hud, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        WIFI = MenuPage(
            name="wifi",
            hotspot=get_hotspot(wifi, interval=1.0),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )
        NETWORK = MenuPage(
            name="network",
            hotspot=get_hotspot(network, interval=1.0,
                                interface="wlan0"
                                ),
            select_action_func=change_menu(Menus.MAIN_MENU),
            cancel_action_func=None
        )

    class MainMenu(Enum):
        DEMO_PROJECT_SELECT = MenuPage(
            name="Project Select",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'mainmenu-select-project.gif'))
                                ),
            select_action_func=change_menu(Menus.PROJECTS),
            cancel_action_func=None
        )

        # Car
        DEMO_PROJECT_CAR = MenuPage(
            name="Demo Project - Car",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-car.gif')),
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # Rover
        DEMO_PROJECT_ROVER = MenuPage(
            name="Demo Project - Rover",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-rover.gif')),
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # Drone
        DEMO_PROJECT_DRONE = MenuPage(
            name="Demo Project - Drone",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-drone.gif')),
                                playback_speed=1
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # Robot
        DEMO_PROJECT_ROBOT = MenuPage(
            name="Demo Project - Robot",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-robot.gif')),
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # Sensor
        DEMO_PROJECT_SENSOR = MenuPage(
            name="Demo Project - Sensor",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-sensor.gif')),
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # Connected to computer
        DEMO_PROJECT_CONNECTED = MenuPage(
            name="Demo Project - Connected",
            hotspot=get_hotspot(image,
                                image_path=path.abspath(path.join(path.dirname(__file__), '..', '..', 'demo',
                                                                  'project-connected.gif'))
                                ),
            select_action_func=None,
            cancel_action_func=None
        )

        # PROJECT_SELECT = MenuPage(
        #     name="Project Select",
        #     hotspot=get_hotspot(main_menu,
        #                         title="Project Select"),
        #     select_action_func=change_menu(Menus.PROJECTS),
        #     cancel_action_func=None
        # )
        # SETTINGS_SELECT = MenuPage(
        #     name="Settings",
        #     hotspot=get_hotspot(main_menu,
        #                         title="Settings"),
        #     select_action_func=None,  # change_menu(Menus.SETTINGS)
        #     cancel_action_func=None
        # )
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
        VNC_CONNECTION = MenuPage(
            name="VNC Connection",
            hotspot=get_hotspot(main_menu,
                                title="VNC Connection"),
            select_action_func=None,  # change_menu(Menus.VNC),
            cancel_action_func=None
        )

    class ProjectSelectMenu:
        @staticmethod
        def generate_pages():
            project_dir = "/home/pi/Desktop/My Remote RPi Projects" if is_pi() else path.expanduser(
                '~/Desktop/My Remote RPi Projects')
            project_pages = list()
            if path.exists(project_dir):
                # For each directory in project path
                project_subdirs = [name for name in sorted(listdir(project_dir))
                                   if path.isdir(path.join(project_dir, name))]
                for project_subdir in project_subdirs:
                    # Get name from path
                    title = project_subdir
                    img_path = get_project_icon(project_dir + "/" + project_subdir)

                    project_page = MenuPage(title, get_hotspot(projects_menu,
                                                               title=title,
                                                               img_path=img_path
                                                               ),
                                            start_stop_project(project_dir + "/" + project_subdir), None)
                    project_pages.append(project_page)
            else:
                title = "No Projects Available"
                img_path = get_project_icon("")

                project_page = MenuPage(title, get_hotspot(projects_menu,
                                                           title=title,
                                                           img_path=img_path
                                                           ),
                                        None, None)
                project_pages.append(project_page)
            return project_pages


def get_project_icon(project_path):
    icon_path = project_path + "/remote_rpi/icon.png"

    if not path.isfile(icon_path):
        icon_path = path.join(path.dirname(__file__), '../../images/pi-top.png')

    return icon_path


def get_menu_enum_class_from_name(menu_name):
    if menu_name == Menus.SYS_INFO:
        return Pages.SysInfoMenu
    elif menu_name == Menus.MAIN_MENU:
        return Pages.MainMenu
    elif menu_name == Menus.PROJECTS:
        return Pages.ProjectSelectMenu
    else:
        _app.stop()
        raise Exception("Unrecognised menu name: " + menu_name.name)


def get_pages(menu_name):
    pages_enum = get_menu_enum_class_from_name(menu_name)

    if hasattr(pages_enum, '__members__'):
        return [page_name.value for page_id, page_name in pages_enum.__members__.items()]
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


def add_infinite_scroll_edge_pages(pages):
    first_page = pages[0]
    last_page = pages[-1]
    pages.append(first_page)
    pages.insert(0, last_page)
    return pages


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
            PTLogger.debug("Removing invalid sys info widget: " + str(widget_name))
            widget_name_list.remove(widget_name)
    return widget_name_list


def get_sys_info_pages_from_config():
    cfg_path = "/etc/pi-top/pt-sys-menu" if is_pi() else path.expanduser("~/.pt-sys-menu")
    cfg_file = cfg_path + "/prefs.cfg"
    page_name_arr = list()
    try:
        with open(cfg_file, 'r') as f:
            page_name_arr = remove_invalid_sys_info_widget_names(f.read().splitlines())
            # Do something if this ends up empty - show a "none selected" screen?
    except FileExistsError:
        # Can be triggered by cfg_path existing as file - fix edge case
        pass
    except (FileNotFoundError, NotADirectoryError):
        # Default
        PTLogger.info("No config file - falling back to default")

    if len(page_name_arr) < 1:
        page_name_arr = ['demo_startup', 'demo_hud']

    PTLogger.info("Sys Info pages: " + str(", ".join(page_name_arr)))

    # Write corrected list back to file
    Path(cfg_path).mkdir(parents=True, exist_ok=True)
    with open(cfg_file, 'w') as f:
        for page_name in page_name_arr:
            f.write("%s\n" % page_name)

    page_id_arr = list()
    for page_name in page_name_arr:
        page_id = get_enum_key_from_value(Menus.SYS_INFO, page_name)
        page_id_arr.append(page_id)

    return page_id_arr
