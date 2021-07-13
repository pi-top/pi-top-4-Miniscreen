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
    wifi as wifi_settings_page,
)
from .widgets.projects import (
    template as projects_menu_page,
    # title as projects_title,
)
from .widgets.error import template as error_page
from .helpers.menu_page_actions import (
    change_pt_further_link_enabled_state,
    change_ssh_enabled_state,
    change_vnc_enabled_state,
    change_wifi_mode,
    read_wifi_mode_state,
    reset_hdmi_configuration,
    start_stop_project,
)

from pitopcommon.logger import PTLogger
from pitopcommon.sys_info import (
    get_pt_further_link_enabled_state,
    get_ssh_enabled_state,
    get_vnc_enabled_state,
)

from enum import Enum
from multiprocessing import Process
from PIL import Image
from os import path, listdir


class Menus(Enum):
    SYS_INFO = 0
    MAIN_MENU = 1
    PROJECTS = 2
    SETTINGS = 3


class MenuPage:

    def __init__(
        self,
        callback_client,
        name,
        hotspot,
        action_func=None,
        menu_to_change_to=None,
    ):
        if action_func is not None:
            assert(menu_to_change_to is None)
        elif menu_to_change_to is not None:
            assert(action_func is None)

        self.__callback_client = callback_client
        self.name = name
        self.hotspot = hotspot
        self.action_func = action_func
        self.menu_to_change_to = menu_to_change_to

        self.action_thread = None

    def is_menu_changer(self):
        return self.menu_to_change_to is not None

    def has_custom_action(self):
        return callable(self.action_func)

    def has_action(self):
        return self.is_menu_changer() or self.has_custom_action()

    def run_action(self):
        if self.is_menu_changer():
            self.__callback_client.change_menu(self.menu_to_change_to)
            return

        if not self.has_custom_action():
            return

        self.action_thread = Process(target=self.action_func)
        self.action_thread.daemon = True
        self.action_thread.start()

        self.__callback_client.start_current_menu_action()


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
                    name="pt_further_link",
                    hotspot=self.__get_hotspot(
                        widget=settings_menu_page,
                        type="pt_further_link",
                        get_state_method=get_pt_further_link_enabled_state,
                    ),
                    action_func=change_pt_further_link_enabled_state,
                ),
                MenuPage(
                    callback_client=self.__callback_client,
                    name="ap",
                    hotspot=self.__get_hotspot(
                        widget=wifi_settings_page,
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
                        get_state_method=None,
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
