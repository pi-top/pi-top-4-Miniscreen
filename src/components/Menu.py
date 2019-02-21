from luma.core.threadpool import threadpool

from components.helpers import MenuHelper
from components.System import device
from ptcommon.logger import PTLogger


pool = threadpool(4)


class Menu:
    """A scrollable viewport of many menu widgets"""

    def __init__(self, device, name):
        """Constructor for Menu"""
        self.pages = list()
        self.name = name
        self.parent = None
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
        elif name == MenuHelper.Menus.SETTINGS:
            self.parent = MenuHelper.Menus.SETTINGS
            pages = MenuHelper.get_pages(MenuHelper.Menus.SETTINGS)
        else:
            raise Exception("Unrecognised menu name")

        set_up_viewport(pages)

    def set_up_viewport(pages):
        self.pages = pages
        self.viewport = MenuHelper.create_viewport(device, self.pages)

    def get_page_y_pos(self, page_index=None):
        if page_index is None:
            page_index = self.page_index
        return page_index * device.height

    def move_instantly_to_page(self, page_index, debug_print=True):
        self.page_index = page_index
        if debug_print:
            PTLogger.info("Moving instantly to " + str(self.get_current_page().name))

    def get_current_page(self):
        return self.pages[self.page_index]

    def last_page_no(self):
        return len(self.pages) - 1

    def should_redraw(self):
        should_wait = False
        for hotspot, xy in self.viewport._hotspots:
            if hotspot.should_redraw() and self.viewport.is_overlapping_viewport(hotspot, xy):
                pool.add_task(hotspot.paste_into, self.viewport._backing_image, xy)
                should_wait = True

        if should_wait:
            pool.wait_completion()

        self.viewport._position = (0, self.get_page_y_pos())
        image_to_display = self.viewport._backing_image.crop(
            box=self.viewport._crop_box()
        )

        if self.last_displayed_image == None:
            self.last_displayed_image = image_to_display
            should_redraw = True
        else:
            image_to_display_pixels = list(image_to_display.getdata())
            last_displayed_image_pixels = list(self.last_displayed_image.getdata())

            image_has_updated = image_to_display_pixels != last_displayed_image_pixels
            self.last_displayed_image = image_to_display if image_has_updated else self.last_displayed_image
            should_redraw = image_has_updated

        return should_redraw

    def redraw_if_necessary(self):
        if self.should_redraw():
            im = self.viewport._backing_image.crop(box=self.viewport._crop_box())
            self.viewport._device.display(im)
            del im

    def get_viewport_height(self):
        return self.viewport.size[1]
