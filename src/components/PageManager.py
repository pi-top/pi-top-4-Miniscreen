from .MenuPage import MenuPage

from .widgets.sys_info import (
    ap,
    batt_level,
    cpu_load,
    ethernet,
    usb,
    wifi,
)
from .widgets.main import template as main_menu_page
from .widgets.settings import (
    template as settings_menu_page,
    title as setting_title,
)
from .widgets.projects import (
    template as projects_menu_page,
    # title as projects_title,
)
from .widgets.error import template as error_page
from .helpers.menu_page_actions import (
    change_further_link_enabled_state,
    change_ssh_enabled_state,
    change_vnc_enabled_state,
    change_wifi_mode,
    read_wifi_mode_state,
    reset_hdmi_configuration,
    start_stop_project,
)

from pitop.common.sys_info import (
    get_further_link_enabled_state,
    get_ssh_enabled_state,
    get_vnc_enabled_state,
)

from enum import Enum
from os import (
    listdir,
    path,
)


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3


class PageManager:
    def __init__(self, device_width, device_height, device_mode, callback_client):
        self.__device_width = device_width
        self.__device_height = device_height
        self.__device_mode = device_mode
        self.__callback_client = callback_client

    def __get_hotspot(self, widget, interval=0.5, **extra_data):
        data = {
            **{
                "width": self.__device_width,
                "height": self.__device_height,
                "mode": self.__device_mode,
                "interval": interval
            },
            **extra_data,
        }
        return widget.Hotspot(**data)

    def get_pages_for_menu(self, menu_id):
        pages = list()
        if menu_id == Menus.SYS_INFO:
            pages = [
                MenuPage(
                    callback_client=self.__callback_client,
                    name="battery",
                    hotspot=self.__get_hotspot(
                        widget=batt_level,
                        interval=1.0,
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="cpu",
                    hotspot=self.__get_hotspot(
                        widget=cpu_load,
                        interval=0.5
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="wifi",
                    hotspot=self.__get_hotspot(
                        widget=wifi,
                        interval=1.0
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="ethernet",
                    hotspot=self.__get_hotspot(
                        widget=ethernet,
                        interval=1.0
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="ap",
                    hotspot=self.__get_hotspot(
                        widget=ap,
                        interval=1.0
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="usb",
                    hotspot=self.__get_hotspot(
                        widget=usb,
                        interval=1.0
                    ),
                    menu_to_change_to=Menus.MAIN_MENU,
                ),
            ]
        elif menu_id == Menus.MAIN_MENU:
            pages = [
                MenuPage(
                    callback_client=self.__callback_client,
                    name="Settings",
                    hotspot=self.__get_hotspot(
                        widget=setting_title,
                        interval=0.5,
                        title="Settings"
                    ),
                    menu_to_change_to=Menus.SETTINGS,
                ),
                # MenuPage(
                #     callback_client=self.__callback_client,
                #     name="Projects",
                #     hotspot=self.__get_hotspot(
                #         widget=projects_title,
                #         interval=0.5,
                #         title="Projects"
                #     ),
                #     menu_to_change_to=Menus.PROJECTS,
                # ),
            ]
        elif menu_id == Menus.SETTINGS:
            pages = [
                MenuPage(
                    callback_client=self.__callback_client,
                    name="ssh_connection",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="ssh",
                        get_state_method=get_ssh_enabled_state,
                    ),
                    action_func=change_ssh_enabled_state,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="vnc_connection",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="vnc",
                        get_state_method=get_vnc_enabled_state,
                    ),
                    action_func=change_vnc_enabled_state,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="further_link",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="further_link",
                        get_state_method=get_further_link_enabled_state,
                    ),
                    action_func=change_further_link_enabled_state,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="ap",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="ap",
                        get_state_method=read_wifi_mode_state,
                    ),
                    action_func=change_wifi_mode,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="hdmi_reset",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="hdmi_reset",
                    ),
                    action_func=reset_hdmi_configuration,
                ),
            ]
        elif menu_id == Menus.PROJECTS:
            project_dir = path.expanduser("~/Desktop/My Projects")
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

                    pages.append(
                        MenuPage(
                            callback_client=self.__callback_client,
                            name=title,
                            hotspot=self.__get_hotspot(
                                widget=projects_menu_page,
                                title=title,
                                project_path=project_path,
                            ),
                            action_func=lambda: start_stop_project(project_path),
                        )
                    )
                if not pages:
                    title = "No Projects Found"

                    pages.append(
                        MenuPage(
                            callback_client=self.__callback_client,
                            name=title,
                            hotspot=self.__get_hotspot(
                                widget=main_menu_page,
                                title=title,
                                image_path=None,
                            ),
                        )
                    )
            else:
                title = "Project Directory"
                second_line = "Not Found"

                pages.append(
                    MenuPage(
                        callback_client=self.__callback_client,
                        name=title,
                        hotspot=self.__get_hotspot(
                            widget=error_page,
                            title=title,
                            second_line=second_line,
                            image_path=None,
                        ),
                    )
                )

        return pages
