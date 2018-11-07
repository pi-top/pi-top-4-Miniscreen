from components.helpers.MenuHelper import MenuHelper
from components.helpers.MenuPageHelper import MenuPageHelper
from components.page import MenuPage


class Menu:
    """A scrollable viewport of many menu MenuPageHelper.Pages.SysInfo."""

    def __init__(self, device, name):
        """Constructor for Menu"""
        self._device = device
        self.pages = []
        self.moving_to_page = False
        self.name = name
        self.parent = None

        if name == MenuHelper.Menus.SYS_INFO:
            page_ids = MenuPageHelper.get_sys_info_page_ids_from_config()
            pages = self.get_menu_pages_from_ids(page_ids)
        elif name == MenuHelper.Menus.MAIN_MENU:
            self.parent = MenuHelper.Menus.SYS_INFO
            page_ids = MenuPageHelper.get_main_menu_page_ids()
            pages = self.get_menu_pages_from_ids(page_ids)
        else:
            raise Exception("Unrecognised menu name")

        self.pages = MenuHelper.add_infinite_scroll_edge_pages(pages)
        self.viewport = MenuHelper.create_viewport(self._device, self.pages)

        self.move_instantly_to_page(1)

    @staticmethod
    def get_menu_pages_from_ids(page_ids):
        pages = []
        for page_id in page_ids:
            pages.append(MenuPage(page_id=page_id, select_action_menu=MenuHelper.Menus.MAIN_MENU))
        return pages

    def get_page_y_pos(self, page_index=None):
        if page_index is None:
            page_index = self.page_index
        return page_index * self._device.height

    def move_instantly_to_page(self, page_index):
        self.page_index = page_index
        self.y_pos = self.get_page_y_pos(self.page_index)

    def go_to_previous_page(self):
        self.page_index = self.page_index - 1

    def go_to_next_page(self):
        self.page_index = self.page_index + 1

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
        arrived_at_screen = (self.y_pos == self.get_page_y_pos())
        if arrived_at_screen:
            if self.moving_to_page:
                self.update_position_if_at_end_of_viewport()
        else:
            self.y_pos = self.y_pos - 1 if self.get_page_y_pos() < self.y_pos else self.y_pos + 1

        self.moving_to_page = not arrived_at_screen
        self.viewport.set_position((0, self.y_pos))

    def get_viewport_height(self):
        return self.viewport.size[1]
