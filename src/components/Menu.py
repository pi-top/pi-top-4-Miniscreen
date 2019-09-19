from luma.core.threadpool import threadpool
from components.helpers import MenuHelper

from ptcommon.sys_info import is_pi
from ptcommon.logger import PTLogger

from ptoled import get_device_instance, reset_device_instance

if is_pi():
    from ptoled import PTOLEDDisplay


pool = threadpool(4)


class Menu:
    def __init__(self, name):
        self.pages = list()
        self.name = name
        self.parent = None
        self.page_index = 0
        self.last_displayed_image = None
        self.force_redraw = False

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
        elif name == MenuHelper.Menus.FIRST_TIME:
            pages = MenuHelper.get_pages(MenuHelper.Menus.FIRST_TIME)
        else:
            raise Exception("Unrecognised menu name")

        self.set_up_viewport(pages)

    def set_up_viewport(self, pages):
        self.pages = pages
        self.viewport = MenuHelper.create_viewport(
            get_device_instance(), self.pages)

    def get_page_y_pos(self, page_index=None):
        if page_index is None:
            page_index = self.page_index
        return page_index * get_device_instance().height

    def move_instantly_to_page(self, page_index, debug_print=True):
        previous_page = self.page_index

        self.page_index = page_index
        if debug_print:
            PTLogger.info("Moving instantly to " +
                          str(self.get_current_page().name))

        self.reset_page(previous_page)

    def reset_page(self, page_index):
        self.get_page(page_index).hotspot.reset()

    def get_page(self, page_index):
        return self.pages[page_index]

    def get_current_page(self):
        return self.get_page(self.page_index)

    def last_page_no(self):
        return len(self.pages) - 1

    def wait_for_any_remaining_viewport_operations(self):
        should_wait = False
        for hotspot, xy in self.viewport._hotspots:
            if hotspot.should_redraw() and self.viewport.is_overlapping_viewport(
                hotspot, xy
            ):
                pool.add_task(hotspot.paste_into,
                              self.viewport._backing_image, xy)
                should_wait = True

        if should_wait:
            pool.wait_completion()

    def should_redraw(self):
        if self.force_redraw:
            PTLogger.info("Forcing a redraw")
            self.force_redraw = False
            return True

        self.viewport._position = (0, self.get_page_y_pos())
        image_to_display = self.viewport._backing_image.crop(
            box=self.viewport._crop_box()
        )

        if self.last_displayed_image is None:
            self.last_displayed_image = image_to_display
            return True
        elif self.new_image_is_different_from_current_image(image_to_display):
            self.last_displayed_image = image_to_display
            return True

        return False

    def new_image_is_different_from_current_image(self, image_to_display):
        return image_to_display != self.last_displayed_image

    def reset_device(self):
        self.force_redraw = True
        PTLogger.info("Resetting device instance...")
        reset_device_instance(exclusive=False)
        if is_pi():
            PTOLEDDisplay().reset()

    def redraw_if_necessary(self):
        self.wait_for_any_remaining_viewport_operations()

        if self.should_redraw():
            im = self.viewport._backing_image.crop(
                box=self.viewport._crop_box())
            get_device_instance().display(im)
            del im

    def get_viewport_height(self):
        return self.viewport.size[1]
