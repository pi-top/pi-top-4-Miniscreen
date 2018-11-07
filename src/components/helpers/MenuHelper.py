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


def _get_hotspot(render_func, widget_width=128, widget_height=64, interval=0.0):
    if float(interval) == 0.0:
        return hotspot(widget_width, widget_height, render_func)
    else:
        return snapshot(widget_width, widget_height, render_func, interval=interval)


def get_hotspot(widget_id):
    if widget_id == Pages.SysInfo.BATTERY:
        return _get_hotspot(batt_level.render, interval=1.0)

    elif widget_id == Pages.SysInfo.UPTIME:
        return _get_hotspot(uptime.render, interval=1.0)

    elif widget_id == Pages.SysInfo.MEMORY:
        return _get_hotspot(memory.render, interval=2.0)

    elif widget_id == Pages.SysInfo.DISK:
        return _get_hotspot(disk.render, interval=2.0)

    elif widget_id == Pages.SysInfo.CPU:
        return _get_hotspot(cpu_load.render, interval=0.5)

    elif widget_id == Pages.SysInfo.CLOCK:
        return _get_hotspot(clock.render, interval=1.0)

    elif widget_id == Pages.SysInfo.HUD:
        return _get_hotspot(hud.render, interval=1.0)

    elif widget_id == Pages.MainMenu.PROJECT_SELECT:
        return _get_hotspot(main_menu.page(title="Projects"), interval=0.0)

    elif widget_id == Pages.MainMenu.SETTINGS_SELECT:
        return _get_hotspot(main_menu.page(title="Settings"), interval=0.0)

    elif widget_id == Pages.MainMenu.WIFI_SETUP_SELECT:
        return _get_hotspot(main_menu.page(title="Wi-Fi Setup"), interval=0.0)

    elif widget_id == Pages.Template.PROJECT_PAGE:
        return _get_hotspot(projects_menu.page(title="My Project"), interval=0.0)


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4


class Pages:
    class SysInfo(Enum):
        get_hotspot = get_hotspot

        BATTERY = MenuPage(hotspot=get_hotspot("battery"), change_menu(Menus.MAIN_MENU))
        UPTIME = MenuPage(hotspot=get_hotspot("uptime"), change_menu(Menus.MAIN_MENU))
        MEMORY = MenuPage(hotspot=get_hotspot("memory"), change_menu(Menus.MAIN_MENU))
        DISK = MenuPage(hotspot=get_hotspot("disk"), change_menu(Menus.MAIN_MENU))
        CPU = MenuPage(hotspot=get_hotspot("cpu"), change_menu(Menus.MAIN_MENU))
        CLOCK = MenuPage(hotspot=get_hotspot("clock"), change_menu(Menus.MAIN_MENU))
        HUD = MenuPage(hotspot=get_hotspot("hud"), change_menu(Menus.MAIN_MENU))
        # NETWORK = MenuPage("network", change_menu(Menus.MAIN_MENU))

    class MainMenu(Enum):
        PROJECT_SELECT = MenuPage(hotspot=get_hotspot("Project Select"), change_menu(Menus.PROJECTS))
        SETTINGS_SELECT = MenuPage(hotspot=get_hotspot("Settings"), change_menu(Menus.SETTINGS))
        WIFI_SETUP_SELECT = MenuPage(hotspot=get_hotspot("Wi-Fi Setup"), change_menu(Menus.WIFI_SETUP))

    class Template(Enum):
        PROJECT_PAGE = MenuPage(hotspot=get_hotspot("Project X"), run_project())

def get_menu_pages_from_ids(page_ids):
    pages = []
    for page_id in page_ids:
        pages.append(MenuPage(hotspot=get_hotspot(page_id), select_action_func=Menus.MAIN_MENU))
    return pages


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
        page_object = page_enum.value
        if page_object["name"] == value:
            return page_enum
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
    else:
        print(widget_id)
        print(Pages.MainMenu.PROJECT_SELECT)
        raise Exception("Not found: '" + widget_id[0] + "'")


def remove_invalid_sys_info_widget_names(widget_name_list):
    valid_page_names = get_pages(Menus.SYS_INFO)
    for widget_name in widget_name_list:
        if widget_name not in valid_page_names:
            widget_name_list.remove(widget_name)
    return widget_name_list


def get_sys_info_page_ids_from_config():
    try:
        with open(os.path.expanduser('~/.carousel'), 'r') as f:
            page_name_arr = remove_invalid_sys_info_widget_names(f.read().splitlines())
            # Do something if this ends up empty - show a "none selected" screen?
    except FileNotFoundError:
        # Default
        print("No config file - falling back to default")
        page_name_arr = ['cpu', 'clock', 'disk']

    # print(page_name_arr)
    # sys.exit()
    page_id_arr = []
    for page_name in page_name_arr:
        page_id = get_enum_key_from_value(Menus.SYS_INFO, page_name)
        page_id_arr.append(page_id)

    return page_id_arr


def get_main_menu_page_ids():
    return get_pages(Menus.MAIN_MENU)