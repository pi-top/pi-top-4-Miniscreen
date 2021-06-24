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
from .widgets.first_time_setup import first_time_setup
from .widgets.error import template as error_page
from .helpers.menu_page_actions import (
    change_ssh_enabled_state,
    change_vnc_enabled_state,
    change_pt_further_link_enabled_state,
    change_ap_mode_enabled_state,
    reset_hdmi_configuration,
    start_stop_project,
)

from pitopcommon.logger import PTLogger
from pitopcommon.sys_info import (
    get_ssh_enabled_state,
    get_vnc_enabled_state,
    get_pt_further_link_enabled_state,
    get_ap_mode_enabled_state,
)

from PIL import Image
from enum import Enum
from os import path, listdir


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3
    WIRELESS_SETTINGS = 4
    FIRST_TIME = 5


class MenuPage:
    """Base view on screen."""

    def __init__(self, name, hotspot, select_action_func, cancel_action_func):
        """Constructor for MenuPage."""
        self.select_action_func = select_action_func
        self.cancel_action_func = cancel_action_func
        self.hotspot = hotspot
        self.name = name


class PageHelper:
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
                    name="battery",
                    hotspot=self.__get_hotspot(
                        widget=batt_level,
                        interval=1.0,
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="cpu",
                    hotspot=self.__get_hotspot(
                        widget=cpu_load,
                        interval=0.5
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="wifi",
                    hotspot=self.__get_hotspot(
                        widget=wifi,
                        interval=1.0
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="ap",
                    hotspot=self.__get_hotspot(
                        widget=ap,
                        interval=1.0
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="ethernet",
                    hotspot=self.__get_hotspot(
                        widget=ethernet,
                        interval=1.0
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.MAIN_MENU),
                    cancel_action_func=None,
                ),
                MenuPage(
                    name="usb",
                    hotspot=self.__get_hotspot(
                        widget=usb,
                        interval=1.0
                    ),
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
                        widget=setting_title,
                        interval=0.5,
                        title="Settings"
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.SETTINGS),
                    cancel_action_func=None,
                ),
                # MenuPage(
                #     name="Projects",
                #     hotspot=self.__get_hotspot(
                #         widget=projects_title,
                #         interval=0.5,
                #         title="Projects"
                #     ),
                #     select_action_func=lambda: self.__callback_client.change_menu(
                #         Menus.PROJECTS),
                #     cancel_action_func=None,
                # ),
            ]
        elif menu_id == Menus.SETTINGS:
            pages = [
                MenuPage(
                    name="ssh_connection",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="ssh",
                        get_state_method=get_ssh_enabled_state,
                    ),
                    select_action_func=lambda: change_ssh_enabled_state(),
                    cancel_action_func=None
                ),
                MenuPage(
                    name="vnc_connection",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="vnc",
                        get_state_method=get_vnc_enabled_state,
                    ),
                    select_action_func=lambda: change_vnc_enabled_state(),
                    cancel_action_func=None
                ),
                MenuPage(
                    name="pt_further_link",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="pt_further_link",
                        get_state_method=get_pt_further_link_enabled_state,
                    ),
                    select_action_func=lambda: change_pt_further_link_enabled_state(),
                    cancel_action_func=None
                ),
                MenuPage(
                    name="wireless",
                    hotspot=self.__get_hotspot(
                        widget=setting_title,
                        title="Wireless",
                        get_state_method=None,
                    ),
                    select_action_func=lambda: self.__callback_client.change_menu(
                        Menus.WIRELESS_SETTINGS),
                    cancel_action_func=None
                ),
                MenuPage(
                    name="hdmi_reset",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="hdmi_reset",
                        get_state_method=None,
                    ),
                    select_action_func=lambda: reset_hdmi_configuration(),
                    cancel_action_func=None
                ),
            ]
        elif menu_id == Menus.FIRST_TIME:
            pages = [
                MenuPage(
                    name="initial_setup",
                    hotspot=self.__get_hotspot(
                        widget=first_time_setup,
                        interval=1.0
                    ),
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
                                widget=projects_menu_page, title=title, project_path=project_path
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
                                widget=main_menu_page, title=title, image_path=None
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
                            widget=error_page,
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

        self.image = Image.new(
            self.__device_mode, (self.__device_width, self.__device_height))

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
        self.__page_index = page_index
        PTLogger.info(f"{self.name}: Moved to page: {self.page.name}")
        self.refresh(force=True)

    @property
    def page(self):
        return self.pages[self.__page_index]

    @property
    def hotspot(self):
        return self.page.hotspot

    def __render_current_hotspot_to_image(self, force=False):
        if force:
            PTLogger.debug(
                f"{self.name}: Forcing redraw of {self.page.name} to image")

        redraw = self.hotspot.should_redraw()
        if redraw:
            PTLogger.debug(
                f"{self.name}: Hotspot {self.page.name} requested a redraw to image")

        if force or redraw:
            self.image = Image.new(
                self.__device_mode, (self.__device_width, self.__device_height))
            # Calls each hotspot's render() function
            self.hotspot.paste_into(self.image, (0, 0))

    def set_current_image_as_rendered(self):
        self.__last_displayed_image = self.image

    def __image_updated(self):
        return self.image != self.__last_displayed_image

    def should_redraw(self):
        if self.__last_displayed_image is None:
            PTLogger.debug(f"{self.name}: Not yet drawn image")
            return True

        if self.__image_updated():
            PTLogger.debug(f"{self.name}: Image updated")
            return True

        PTLogger.debug(f"{self.name}: Nothing to redraw")
        return False

    def refresh(self, force=False):
        if force:
            self.hotspot.reset()
        self.__render_current_hotspot_to_image(force)
