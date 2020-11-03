from components.helpers import MenuHelper

from pitop.core.sys_info import is_pi
from pitop.core.logger import PTLogger

from ptoled import get_device_instance, reset_device_instance

if is_pi():
    from ptoled import PTOLEDDisplay


class Menu:
    def __init__(self, name):
        self.pages = list()
        self.name = name
        self.parent = None
        self.page_index = 0
        self.last_displayed_image = None

        if self.name == MenuHelper.Menus.SYS_INFO:
            pages = MenuHelper.get_sys_info_pages()
        elif self.name == MenuHelper.Menus.MAIN_MENU:
            self.parent = MenuHelper.Menus.SYS_INFO
            pages = MenuHelper.get_pages(MenuHelper.Menus.MAIN_MENU)
        elif self.name == MenuHelper.Menus.PROJECTS:
            self.parent = MenuHelper.Menus.MAIN_MENU
            pages = MenuHelper.get_pages(MenuHelper.Menus.PROJECTS)
        elif self.name == MenuHelper.Menus.SETTINGS:
            self.parent = MenuHelper.Menus.SETTINGS
            pages = MenuHelper.get_pages(MenuHelper.Menus.SETTINGS)
        elif self.name == MenuHelper.Menus.FIRST_TIME:
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

    def move_instantly_to_page(self, page_index):
        self.page_index = page_index
        PTLogger.info("Moving instantly to " +
                      str(self.get_current_page().name))

        self.get_current_hotspot().reset()
        self.refresh()

    def get_current_hotspot(self):
        return self.get_page(self.page_index).hotspot

    def get_page(self, page_index):
        return self.pages[page_index]

    def get_current_page(self):
        return self.get_page(self.page_index)

    def last_page_no(self):
        return len(self.pages) - 1

    def refresh(self, force=False):
        if force:
            self.get_current_hotspot().reset()
        self.render_current_hotspot_to_viewport(force)
        self.update_oled(force=force)

    def render_current_hotspot_to_viewport(self, force=False):
        self.render_hotspot_to_viewport(self.page_index, force)

    def render_hotspot_to_viewport(self, page_index, force=False):
        hotspot, xy = self.viewport._hotspots[page_index]
        if force or hotspot.should_redraw():
            # Calls each hotspot's render() function
            hotspot.paste_into(self.viewport._backing_image, xy)

    def should_redraw(self):
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
        self.refresh(force=True)
        PTLogger.info("Resetting device instance...")
        reset_device_instance(exclusive=False)
        if is_pi():
            PTOLEDDisplay().reset()
        self.update_oled(force=True)

    def update_oled(self, force=False):
        if force:
            PTLogger.debug("Forcing redraw")

        if force or self.should_redraw():
            PTLogger.debug("Updating image on OLED display")
            im = self.viewport._backing_image.crop(
                box=self.viewport._crop_box())
            get_device_instance().display(im)
            del im

    def get_viewport_height(self):
        return self.viewport.size[1]
