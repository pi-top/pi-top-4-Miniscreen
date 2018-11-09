from enum import Enum
from luma.core.virtual import viewport
from components.Page import MenuPage
from components.widgets.sys_info import batt_level, uptime, memory, disk, cpu_load, clock, hud
from components.widgets.main import template as main_menu
from components.widgets.projects import template as projects_menu
import os.path
from components.Device import device

from luma.core.virtual import snapshot, hotspot
import os

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
        _app.start_stop_project(path_to_project)
    return run


def get_hotspot(render_func, interval=0.0):
    if float(interval) == 0.0:
        return hotspot(device.width, device.height, render_func)
    else:
        return snapshot(device.width, device.height, render_func, interval=interval)


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4


class Pages:
    class SysInfoMenu(Enum):
        BATTERY = MenuPage("battery", get_hotspot(batt_level.render, interval=1.0), change_menu(Menus.MAIN_MENU))
        UPTIME = MenuPage("uptime", get_hotspot(uptime.render, interval=1.0), change_menu(Menus.MAIN_MENU))
        MEMORY = MenuPage("memory", get_hotspot(memory.render, interval=2.0), change_menu(Menus.MAIN_MENU))
        DISK = MenuPage("disk", get_hotspot(disk.render, interval=2.0), change_menu(Menus.MAIN_MENU))
        CPU = MenuPage("cpu", get_hotspot(cpu_load.render, interval=0.5), change_menu(Menus.MAIN_MENU))
        CLOCK = MenuPage("clock", get_hotspot(clock.render, interval=1.0), change_menu(Menus.MAIN_MENU))
        HUD = MenuPage("hud", get_hotspot(hud.render, interval=1.0), change_menu(Menus.MAIN_MENU))
        # NETWORK = MenuPage("network", change_menu(Menus.MAIN_MENU))

    class MainMenu(Enum):
        PROJECT_SELECT = MenuPage(
            "Project Select",
            get_hotspot(
                main_menu.page(title="Project Select"), interval=0.0
            ),
            change_menu(Menus.PROJECTS)
        )
        SETTINGS_SELECT = MenuPage(
            "Settings",
            get_hotspot(
                main_menu.page(title="Settings"), interval=0.0
            ),
            # change_menu(Menus.SETTINGS)
            None
        )
        WIFI_SETUP_SELECT = MenuPage(
            "Wi-Fi Setup",
            get_hotspot(
                main_menu.page(title="Wi-Fi Setup"), interval=0.0
            ),
            # change_menu(Menus.WIFI_SETUP)
            None
        )

    class ProjectSelectMenu:
        @staticmethod
        def generate_pages():
            project_dir = os.path.expanduser('~/Desktop/My Remote RPi Projects')

            project_pages = list()
            if os.path.exists(project_dir):
                # For each directory in project path
                project_subdirs = [name for name in sorted(os.listdir(project_dir))
                        if os.path.isdir(os.path.join(project_dir, name))]
                for project_subdir in project_subdirs:
                    # Get name from path
                    title = project_subdir
                    img_path = get_project_icon(project_dir + "/" + project_subdir)

                    project_page = MenuPage(title,
                        get_hotspot(
                            projects_menu.project(title=title, img_path=img_path), interval=0.0
                        ),
                        start_stop_project(project_dir + "/" + project_subdir)
                    )
                    project_pages.append(project_page)
            else:
                title = "No Projects Available"
                img_path = get_project_icon("")

                project_page = MenuPage(title,
                                        get_hotspot(
                                            projects_menu.project(title=title, img_path=img_path), interval=0.0
                                        ),
                                        None
                                        )
                project_pages.append(project_page)
            return project_pages


def get_project_icon(project_path):
    icon_path = project_path + "/remote_rpi/icon.png"

    if not os.path.isfile(icon_path):
        icon_path = os.path.join(os.path.dirname(__file__), '../../images/pi-top.png')

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
        widget = page.hotspot
        virtual.add_hotspot(widget, (0, created_viewport_height))
        created_viewport_height += widget.height

    return virtual

    # Commented out until merged into one widget

    # elif widget_name == "network":
    #     net_wlan = get_hotspot(network.stats("wlan0"), interval=2.0, widget_height=22)
    #     net_eth = get_hotspot(network.stats("eth0"), interval=2.0, widget_height=21)
    #     net_lo = get_hotspot(network.stats("lo"), interval=2.0, widget_height=21)
    #     widgets_obj_arr.append(net_wlan)
    #     widgets_obj_arr.append(net_eth)
    #     widgets_obj_arr.append(net_lo)


def remove_invalid_sys_info_widget_names(widget_name_list):
    for widget_name in widget_name_list:
        if widget_name not in (page.name for page in get_pages(Menus.SYS_INFO)):
            print("Removing " + str(widget_name))
            widget_name_list.remove(widget_name)
    return widget_name_list


def get_sys_info_pages_from_config():
    try:
        with open(os.path.expanduser('~/.carousel'), 'r') as f:
            page_name_arr = remove_invalid_sys_info_widget_names(f.read().splitlines())
            # Do something if this ends up empty - show a "none selected" screen?
    except FileNotFoundError:
        # Default
        print("No config file - falling back to default")
        page_name_arr = ['cpu', 'clock', 'disk']

    page_id_arr = list()
    for page_name in page_name_arr:
        page_id = get_enum_key_from_value(Menus.SYS_INFO, page_name)
        page_id_arr.append(page_id)

    return page_id_arr
