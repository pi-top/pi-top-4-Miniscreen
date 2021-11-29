import logging

from ..event import AppEvents, post_event
from ..generators import scroll_to

logger = logging.getLogger(__name__)


class Menu:
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, pages, name="Unnamed Menu"):
        assert len(pages) > 0
        self.size = size
        self.pages = pages
        self.name = name
        self._page_index = 0

    @property
    def current_page(self):
        return self.pages[self.page_index]

    @property
    def page_index(self):
        return self._page_index

    @page_index.setter
    def page_index(self, idx):
        if self.page_index == idx:
            return
        prev_page_index = self.page_index
        self._page_index = idx
        self.scroll_coordinate_generator = scroll_to(
            min_value=prev_page_index * self.size[1],
            max_value=self.page_index * self.size[1],  # sum of height of previous pages
            resolution=self.SCROLL_PX_RESOLUTION,
        )

    ###############################
    # Position - immediate/scroll #
    ###############################
    # Ignore scrolling behavior
    def move_to_page_pos(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.size[1]

    # Set page, but still require scrolling
    def set_page_to_previous(self):
        def get_previous_page_index():
            if self.page_index == 0:
                return self.page_index

            return self.page_index - 1

        previous_index = self.page_index
        self.page_index = get_previous_page_index()
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    def set_page_to_next(self):
        def get_next_page_index():
            if self.page_index == len(self.pages) - 1:
                return self.page_index

            return self.page_index + 1

        previous_index = self.page_index
        self.page_index = get_next_page_index()
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    ###########################
    # Child/parent navigation #
    ###########################

    def publish_child_menu_event(self):
        if not self.has_child_menu:
            return
        post_event(AppEvents.GO_TO_CHILD_MENU, self.current_page.child_menu)

    def go_to_parent_menu(self):
        logger.info("Going to parent")
        post_event(AppEvents.GO_TO_PARENT_MENU, self)

    @property
    def has_child_menu(self):
        return self.current_page.child_menu is not None
