from components.helpers import MenuHelper
from components.System import device
from ptcommon.logger import PTLogger


class Menu:
    """A scrollable viewport of many menu widgets"""

    def __init__(self, device, name):
        """Constructor for Menu"""
        self.pages = list()
        self.moving_to_page = False
        self.name = name
        self.parent = None
        self.y_pos = 0
        self.page_index = 0
        self.last_displayed_image = None

        if name == MenuHelper.Menus.SYS_INFO:
            pages = MenuHelper.get_sys_info_pages_from_config()
        elif name == MenuHelper.Menus.MAIN_MENU:
            self.parent = MenuHelper.Menus.SYS_INFO
            pages = MenuHelper.get_pages(MenuHelper.Menus.MAIN_MENU)
        elif name == MenuHelper.Menus.PROJECTS:
            self.parent = MenuHelper.Menus.MAIN_MENU
            pages = MenuHelper.get_pages(MenuHelper.Menus.PROJECTS)
        else:
            raise Exception("Unrecognised menu name")

        # Enable scrolling if there is more than one page
        self.scroll_enabled = len(pages) > 1

        if self.scroll_enabled:
            self.pages = MenuHelper.add_infinite_scroll_edge_pages(pages)
        else:
            self.pages = pages

        self.viewport = MenuHelper.create_viewport(device, self.pages)

        if self.scroll_enabled:
            self.move_instantly_to_page(1, debug_print=False)

    def get_page_y_pos(self, page_index=None):
        if page_index is None:
            page_index = self.page_index
        return page_index * device.height

    def move_instantly_to_first_page(self, debug_print=True):
        if self.scroll_enabled:
            self.move_instantly_to_page(1, debug_print)
        else:
            self.move_instantly_to_page(0, debug_print)

    def move_instantly_to_page(self, page_index, debug_print=True):
        self.page_index = page_index
        self.y_pos = self.get_page_y_pos(self.page_index)
        if debug_print:
            PTLogger.info("Moving instantly to " + str(self.get_current_page().name))

    def set_page_to_previous(self):
        self.page_index = self.page_index - 1
        PTLogger.info("Setting page to " + str(self.get_current_page().name))

    def set_page_to_next(self):
        self.page_index = self.page_index + 1
        PTLogger.info("Setting page to " + str(self.get_current_page().name))

    def get_current_page(self):
        return self.pages[self.page_index]

    def second_to_last_page_no(self):
        return len(self.pages) - 2

    def last_page_no(self):
        return len(self.pages) - 1

    def update_position_if_at_end_of_viewport(self):
        if self.page_index == 0:
            self.move_instantly_to_page(self.second_to_last_page_no())
        elif self.page_index == self.last_page_no():
            self.move_instantly_to_page(1)

    def update_position_based_on_state(self):
        if self.scroll_enabled:
            arrived_at_screen = self.y_pos == self.get_page_y_pos()
            if arrived_at_screen:
                if self.moving_to_page:
                    PTLogger.debug("Arrived at " + str(self.get_current_page().name))
                    self.update_position_if_at_end_of_viewport()
            else:
                self.y_pos = (
                    (self.y_pos - 1)
                    if (self.get_page_y_pos() < self.y_pos)
                    else (self.y_pos + 1)
                )

            self.moving_to_page = not arrived_at_screen


        self.viewport._position = (0, self.y_pos)
        image_to_display = self.viewport._backing_image.crop(
            box=self.viewport._crop_box()
        )

        if self.last_displayed_image == None:
            draw_to_display = True
        else:
            image_to_display_pixels = list(image_to_display.getdata())
            last_displayed_image_pixels = list(self.last_displayed_image.getdata())

            image_has_updated = (
                image_to_display_pixels
                != last_displayed_image_pixels
            )
            draw_to_display = image_has_updated

        if draw_to_display:
            self.last_displayed_image = image_to_display
            # New pixelmap - update display
            self.viewport.refresh()

    def get_viewport_height(self):
        return self.viewport.size[1]
