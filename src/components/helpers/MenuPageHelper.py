from components.helpers.MenuHelper import MenuHelper
from components.widgets.sys_info import batt_level, uptime, memory, disk, cpu_load, clock, hud
from components.widgets.main import template as main_menu
from components.widgets.projects import template as projects_menu

from luma.core.virtual import snapshot, hotspot
from enum import Enum
import os


class MenuPageHelper:
    """A widget that takes up the full size of the display. Component of a menu."""

    class Pages:
        # Note - all enum values must be different!
        class SysInfo(Enum):
            # These are strings so that they can be enabled/disabled via a config file
            BATTERY = "battery"
            UPTIME = "uptime"
            MEMORY = "memory"
            DISK = "disk"
            CPU = "cpu"
            CLOCK = "clock"
            HUD = "hud"
            # NETWORK = "network"

        class MainMenu(Enum):
            PROJECT_SELECT = 0
            SETTINGS_SELECT = 1
            WIFI_SETUP_SELECT = 2

        class Template(Enum):
            PROJECT_PAGE = 3

    @staticmethod
    def get_menu_enum_class_from_name(menu_name):
        if menu_name == MenuHelper.Menus.SYS_INFO:
            return MenuPageHelper.Pages.SysInfo
        elif menu_name == MenuHelper.Menus.MAIN_MENU:
            return MenuPageHelper.Pages.MainMenu
        else:
            raise Exception("Unrecognised menu name: " + menu_name)

    @staticmethod
    def get_page_names(menu_name):
        pages_enum = MenuPageHelper.get_menu_enum_class_from_name(menu_name)
        return[page_name.value for page_id, page_name in pages_enum.__members__.items()]

    @staticmethod
    def get_page_ids(menu_name):
        pages_enum = MenuPageHelper.get_menu_enum_class_from_name(menu_name)
        return pages_enum.__members__.items()

    @staticmethod
    def get_enum_key_from_value(menu_name, value):
        pages_enum = MenuPageHelper.get_menu_enum_class_from_name(menu_name)
        for page_id, page_name in pages_enum.__members__.items():
            if page_name.value == value:
                return page_name
        raise Exception("Unable to find enum key matching value: " + str(value))

    @staticmethod
    def _get_hotspot(render_func, widget_width=128, widget_height=64, interval=0.0):
        if float(interval) == 0.0:
            return hotspot(widget_width, widget_height, render_func)
        else:
            return snapshot(widget_width, widget_height, render_func, interval=interval)

    @staticmethod
    def get_hotspot(widget_id):
        if widget_id == MenuPageHelper.Pages.SysInfo.BATTERY:
            return MenuPageHelper._get_hotspot(batt_level.render, interval=1.0)

        elif widget_id == MenuPageHelper.Pages.SysInfo.UPTIME:
            return MenuPageHelper._get_hotspot(uptime.render, interval=1.0)

        elif widget_id == MenuPageHelper.Pages.SysInfo.MEMORY:
            return MenuPageHelper._get_hotspot(memory.render, interval=2.0)

        elif widget_id == MenuPageHelper.Pages.SysInfo.DISK:
            return MenuPageHelper._get_hotspot(disk.render, interval=2.0)

        elif widget_id == MenuPageHelper.Pages.SysInfo.CPU:
            return MenuPageHelper._get_hotspot(cpu_load.render, interval=0.5)

        elif widget_id == MenuPageHelper.Pages.SysInfo.CLOCK:
            return MenuPageHelper._get_hotspot(clock.render, interval=1.0)

        elif widget_id == MenuPageHelper.Pages.SysInfo.HUD:
            return MenuPageHelper._get_hotspot(hud.render, interval=1.0)

        elif widget_id == MenuPageHelper.Pages.MainMenu.PROJECT_SELECT:
            return MenuPageHelper._get_hotspot(main_menu.page(title="Projects"), interval=0.0)

        elif widget_id == MenuPageHelper.Pages.MainMenu.SETTINGS_SELECT:
            return MenuPageHelper._get_hotspot(main_menu.page(title="Settings"), interval=0.0)

        elif widget_id == MenuPageHelper.Pages.MainMenu.WIFI_SETUP_SELECT:
            return MenuPageHelper._get_hotspot(main_menu.page(title="Wi-Fi Setup"), interval=0.0)

        elif widget_id == MenuPageHelper.Pages.Template.PROJECT_PAGE:
            return MenuPageHelper._get_hotspot(projects_menu.page(title="My Project"), interval=0.0)

        # Commented out until merged into one widget

        # elif widget_name == "network":
        #     net_wlan = get_hotspot(network.stats("wlan0"), interval=2.0, widget_height=22)
        #     net_eth = get_hotspot(network.stats("eth0"), interval=2.0, widget_height=21)
        #     net_lo = get_hotspot(network.stats("lo"), interval=2.0, widget_height=21)
        #     widgets_obj_arr.append(net_wlan)
        #     widgets_obj_arr.append(net_eth)
        #     widgets_obj_arr.append(net_lo)
        else:
            raise Exception("Not found: '" + widget_id[0] + "'")

    @staticmethod
    def remove_invalid_sys_info_widget_names(widget_name_list):
        valid_page_names = MenuPageHelper.get_page_names(MenuHelper.Menus.SYS_INFO)
        for widget_name in widget_name_list:
            if widget_name not in valid_page_names:
                widget_name_list.remove(widget_name)
        return widget_name_list

    @staticmethod
    def get_sys_info_page_ids_from_config():
        try:
            with open(os.path.expanduser('~/.carousel'), 'r') as f:
                page_name_arr = MenuPageHelper.remove_invalid_sys_info_widget_names(f.read().splitlines())
                # Do something if this ends up empty - show a "none selected" screen?
        except FileNotFoundError:
            # Default
            print("No config file - falling back to default")
            page_name_arr = ['cpu', 'clock', 'disk']

        page_id_arr = []
        for page_name in page_name_arr:
            page_id = MenuPageHelper.get_enum_key_from_value(MenuHelper.Menus.SYS_INFO, page_name)
            page_id_arr.append(page_id)

        return page_id_arr

    @staticmethod
    def get_main_menu_page_ids():
        page_id_arr = []

        page_name_arr = MenuPageHelper.get_page_names(MenuHelper.Menus.MAIN_MENU)
        for page_name in page_name_arr:
            page_id = MenuPageHelper.get_enum_key_from_value(MenuHelper.Menus.MAIN_MENU, page_name)
            page_id_arr.append(page_id)

        return page_id_arr