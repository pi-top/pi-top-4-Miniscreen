from .PageManager import (
    Menus,
    PageManager,
)

from pitopcommon.logger import PTLogger

from PIL import Image


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
        self.pages = PageManager(
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
        return self.pages[self.page_number]

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
