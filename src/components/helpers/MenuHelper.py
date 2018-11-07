from enum import Enum
from luma.core.virtual import viewport
from components.page import MenuPage
from components.widgets.sys_info import batt_level, uptime, memory, disk, cpu_load, clock, hud
from components.widgets.main import template as main_menu
from components.widgets.projects import template as projects_menu

from luma.core.virtual import snapshot, hotspot
import os

_app = None


def set_app(top_level_app_obj):
    global _app
    _app = top_level_app_obj


def change_menu(menu_id):
    # if _app is not None:
    def run():
        _app.change_menu(menu_id)
    return run
    # else:
        # raise Exception("Top-level app is not available")


def run_project(project_title):
    # if _app is not None:
    def run():
        # _app.change_menu(menu_id)
        pass
    return run
    # else:
        # raise Exception("Top-level app is not available")


def get_hotspot(render_func, widget_width=128, widget_height=64, interval=0.0):
    if float(interval) == 0.0:
        return hotspot(widget_width, widget_height, render_func)
    else:
        return snapshot(widget_width, widget_height, render_func, interval=interval)

class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4


class Pages:
    class SysInfo(Enum):
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
            get_hotspot(main_menu.page(title="Project Select"), interval=0.0), change_menu(Menus.PROJECTS)
        )
        SETTINGS_SELECT = MenuPage(
            "Settings",
            get_hotspot(main_menu.page(title="Settings"), interval=0.0), change_menu(Menus.SETTINGS)
        )
        WIFI_SETUP_SELECT = MenuPage(
            "Wi-Fi Setup",
            get_hotspot(main_menu.page(title="Wi-Fi Setup"), interval=0.0), change_menu(Menus.WIFI_SETUP)
        )

    class Template(Enum):
        PROJECT_PAGE = MenuPage(
            "My Project",
            get_hotspot(projects_menu.project(title="My Project"), interval=0.0), run_project("lol")
        )


def get_menu_enum_class_from_name(menu_name):
    if menu_name == Menus.SYS_INFO:
        return Pages.SysInfo
    elif menu_name == Menus.MAIN_MENU:
        return Pages.MainMenu
    else:
        raise Exception("Unrecognised menu name: " + menu_name)


def get_pages(menu_name):
    pages_enum = get_menu_enum_class_from_name(menu_name)
    return [page_name.value for page_id, page_name in pages_enum.__members__.items()]


def get_page_ids(menu_name):
    pages_enum = get_menu_enum_class_from_name(menu_name)
    return pages_enum.__members__.items()


def get_enum_key_from_value(menu_name, value):
    pages_enum = get_menu_enum_class_from_name(menu_name)
    for page_id, page_enum in pages_enum.__members__.items():
        page = page_enum.value
        if page.name == value:
            return pages_enum[page_id].value
    raise Exception("Unable to find enum key matching value: " + value)


def add_infinite_scroll_edge_pages(pages):
    pages.insert(0, pages[-1])
    pages.append(pages[0])
    return pages


def create_viewport(device, pages):
    viewport_height = sum(page.hotspot.height for page in pages) + (2 * device.height)
    virtual = viewport(device, width=device.width, height=viewport_height)

    # Start at second page, so that last entry can be added to the start for scrolling
    created_viewport_height = device.height
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

    page_id_arr = []
    for page_name in page_name_arr:
        page_id = get_enum_key_from_value(Menus.SYS_INFO, page_name)
        page_id_arr.append(page_id)

    return page_id_arr


def get_main_menu_pages():
    return get_pages(Menus.MAIN_MENU)