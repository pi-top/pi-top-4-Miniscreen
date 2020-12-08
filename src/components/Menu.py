from .components.Page import MenuPage
from .components.widgets.sys_info import (
    batt_level,
    cpu_load,
    wifi,
    usb,
    ethernet
)
from .components.widgets.main import template as main_menu_page
from .components.widgets.settings import (
    template as settings_menu_page,
    settings as setting_title,
)
from .components.widgets.projects import template as projects_menu_page
from .components.widgets.first_time_setup import first_time_setup
from .components.widgets.error import template as error_page
from .components.helpers.menu_page_actions import (
    change_ssh_enabled_state,
    change_vnc_enabled_state,
    change_pt_further_link_enabled_state,
    reset_hdmi_configuration,
    start_stop_project,
)

from pitopcommon.logger import PTLogger
from pitopcommon.sys_info import (
    get_ssh_enabled_state,
    get_vnc_enabled_state,
    get_pt_further_link_enabled_state,
)

from PIL import Image
from enum import Enum
from os import path, listdir


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIFI_SETUP = 4
    FIRST_TIME = 5


class PageHelper:
    def __init__(self, device_width, device_height, device_mode, callback_client):
        self.__device_width = device_width
        self.__device_height = device_height
        self.__device_mode = device_mode
        self.__callback_client = callback_client

    def __get_hotspot(self, widget, interval=0.0, **extra_data):
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
                    name="battery",
                    hotspot=self.__get_hotspot(
                        batt_level,
                        interval=1.0,
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="cpu",
                    hotspot=self.__get_hotspot(cpu_load, interval=0.5),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="wifi",
                    hotspot=self.__get_hotspot(wifi, interval=1.0),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="ethernet",
                    hotspot=self.__get_hotspot(ethernet, interval=1.0),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="usb",
                    hotspot=self.__get_hotspot(usb, interval=1.0),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
            ]
        elif menu_id == Menus.MAIN_MENU:
            pages = [
                MenuPage(
                    name="Settings",
                    hotspot=self.__get_hotspot(
                        setting_title, title="Settings", interval=1.0),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.SETTINGS),
                    cancel_action_func=None,
                ),
            ]
        elif menu_id == Menus.SETTINGS:
            pages = [
                MenuPage(
                    name="ssh_connection",
                    hotspot=self.__get_hotspot(
                        settings_menu_page,
                        type="ssh",
                        interval=1.0,
                        get_state_method=get_ssh_enabled_state,
                    ),
                    select_action_func=lambda: change_ssh_enabled_state(),
                    cancel_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                ),
                MenuPage(
                    name="vnc_connection",
                    hotspot=self.__get_hotspot(
                        settings_menu_page,
                        type="vnc",
                        interval=1.0,
                        get_state_method=get_vnc_enabled_state,
                    ),
                    select_action_func=lambda: change_vnc_enabled_state(),
                    cancel_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                ),
                MenuPage(
                    name="pt_further_link",
                    hotspot=self.__get_hotspot(
                        settings_menu_page,
                        type="pt_further_link",
                        interval=1.0,
                        get_state_method=get_pt_further_link_enabled_state,
                    ),
                    select_action_func=lambda: change_pt_further_link_enabled_state(),
                    cancel_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                ),
                MenuPage(
                    name="hdmi_reset",
                    hotspot=self.__get_hotspot(
                        settings_menu_page,
                        type="hdmi_reset",
                        interval=0.0,
                        get_state_method=None,
                    ),
                    select_action_func=lambda: reset_hdmi_configuration(),
                    cancel_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                ),
            ]
        elif menu_id == Menus.FIRST_TIME:
            pages = [
                MenuPage(
                    name="initial_setup",
                    hotspot=self.__get_hotspot(first_time_setup, interval=1),
                    select_action_func=None,
                    cancel_action_func=None,
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
                            title,
                            self.__get_hotspot(
                                projects_menu_page, title=title, project_path=project_path
                            ),
                            start_stop_project(project_path),
                            None,
                        )
                    )
                if not pages:
                    title = "No Projects Found"

                    pages.append(
                        MenuPage(
                            title,
                            self.__get_hotspot(
                                main_menu_page, title=title, image_path=None
                            ),
                            None,
                            None,
                        )
                    )
            else:
                title = "Project Directory"
                second_line = "Not Found"

                pages.append(
                    MenuPage(
                        title,
                        self.__get_hotspot(
                            error_page,
                            title=title,
                            second_line=second_line,
                            image_path=None,
                        ),
                        None,
                        None,
                    )
                )

        return pages


class Menu:
    def __init__(self, name, device_width, device_height, device_mode, callback_client):
        self.name = name
        self.parent = None
        self.pages = list()

        if self.name == Menus.MAIN_MENU:
            self.parent = Menus.SYS_INFO

        elif self.name == Menus.PROJECTS:
            self.parent = Menus.MAIN_MENU

        elif self.name == Menus.SETTINGS:
            self.parent = Menus.MAIN_MENU

        self.__device_width = device_width
        self.__device_height = device_height
        self.__device_mode = device_mode

        self.__callback_client = callback_client

        self.__page_index = 0
        self.__last_displayed_image = None

        self.image = Image.new(device_mode, (device_width, device_height))

        self.update_pages()

    def update_pages(self):
        self.pages = PageHelper(
            self.__device_width,
            self.__device_height,
            self.__device_mode,
            self.__callback_client
        ).get_pages_for_menu(self.name)

    @property
    def page_number(self):
        return self.__page_index

    @page_number.setter
    def page_number(self, page_index):
        PTLogger.info(f"Moving page: {self.page.name}")

        self.__page_index = page_index
        self.refresh(force=True)

    @property
    def page(self):
        return self.pages[self.__page_index]

    @property
    def hotspot(self):
        return self.page.hotspot

    def __render_current_hotspot_to_image(self, force=False):
        if force or self.hotspot.should_redraw():
            # Calls each hotspot's render() function
            PTLogger.info(f"{self.page.name} - pasted into")
            self.hotspot.paste_into(self.image, (0, 0))

    def should_redraw(self):
        not_yet_shown = self.__last_displayed_image is None
        image_updated = self.image != self.__last_displayed_image
        if image_updated:
            PTLogger.info("Image updated")
        return not_yet_shown or image_updated

    def refresh(self, force=False):
        if force:
            self.hotspot.reset()
        self.__render_current_hotspot_to_image(force)
