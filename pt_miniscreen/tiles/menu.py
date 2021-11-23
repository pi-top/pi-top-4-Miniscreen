import logging

from ..config import ConfigFactory
from ..config.classes.menu_edge_behaviour import MenuEdgeBehaviour
from ..generators import scroll_to
from .event import AppEvents, post_event
from .viewport import ViewportTile

logger = logging.getLogger(__name__)


class MenuTile(ViewportTile):
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, mode):
        super().__init__(
            size=size,
            viewport_size=(size[0], size[1] * len(config.children)),
            mode=mode,
            window_position=(0, 0),
        )

        self.page_index = 0
        self.y_pos = 0

        self.parent_goes_to_first_page = config.parent_goes_to_first_page
        self.top_edge = config.top_edge
        self.bottom_edge = config.bottom_edge
        self.title_bar = config.title_bar

        config_factory = ConfigFactory(self.size, self.mode)

        self.pages = list()
        for page_name, page_config in config.children.items():
            self.pages.append(config_factory.get(page_config))

    #########
    # Pages #
    #########
    @property
    def current_page(self):
        return self.pages[self.page_index]

    def move_to_page(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.height

    ##########
    # Scroll #
    ##########
    @property
    def needs_to_scroll(self):
        final_y_pos = self.page_index * self.current_page.height
        return self.y_pos != final_y_pos

    def update_scroll_position(self):
        if not self.needs_to_scroll:
            return

        try:
            value = next(self.scroll_coordinate_generator)
            self.y_pos = value
        except StopIteration:
            pass

    ###########################
    # Child/parent navigation #
    ###########################
    def go_to_child_menu(self):
        new_menu = self.child_menu
        if not new_menu:
            return

        logger.info("Current menu's page has child menu - setting menu to child")

        for k, v in new_menu.items():
            self.menus[k] = v

        menu_tile_id = list(new_menu.keys())[0]
        post_event(AppEvents.GO_TO_CHILD_MENU, menu_tile_id)

        if self.menu_tile.parent_goes_to_first_page:
            self.menu_tile.move_to_page(0)

        self.should_redraw_event.set()

    def go_to_parent_menu(self):
        post_event(AppEvents.GO_TO_PARENT_MENU)
        self.should_redraw_event.set()

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        if self.child_menu:
            self._go_to_child_menu()
        else:
            post_event(AppEvents.BUTTON_ACTION_START)
            self.on_select_press()

    def handle_cancel_btn(self):
        # TODO: handle going back to parent
        # if MenuTileConfigManager.menu_id_has_parent(self.menus, self.menu_tile_id):
        # self.go_to_parent_menu()
        pass

    def handle_up_btn(self):
        self.menu._set_page_to_previous()
        if self.menu.needs_to_scroll:
            self.should_redraw_event.set()

    def handle_down_btn(self):
        self.menu._set_page_to_next()
        if self.menu.needs_to_scroll:
            self.should_redraw_event.set()

    ############
    # Internal #
    ############
    def _set_page_index_to(self, page_index):
        if self.page_index == page_index:
            return
        self.page_index = page_index
        self.scroll_coordinate_generator = scroll_to(
            min_value=self.y_pos,
            max_value=self.page_index * self.height,
            resolution=self.SCROLL_PX_RESOLUTION,
        )

    def _set_page_to_previous(self):
        if self.needs_to_scroll:
            return

        previous_index = self.page_index
        self._set_page_index_to(self._get_previous_page_index())
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    def _set_page_to_next(self):
        if self.needs_to_scroll:
            return

        previous_index = self.page_index
        self._set_page_index_to(self._get_next_page_index())
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    def _get_previous_page_index(self):
        if self.page_index == 0:
            if self.top_edge == MenuEdgeBehaviour.NONE:
                return self.page_index

            elif self.top_edge == MenuEdgeBehaviour.BOUNCE:
                return self._get_next_page_index()

            elif self.top_edge == MenuEdgeBehaviour.LOOP:
                return len(self.pages) - 1

        return self.page_index - 1

    def _get_next_page_index(self):
        if self.page_index == len(self.pages) - 1:
            if self.bottom_edge == MenuEdgeBehaviour.NONE:
                return self.page_index

            elif self.bottom_edge == MenuEdgeBehaviour.BOUNCE:
                return self._get_previous_page_index()

            elif self.bottom_edge == MenuEdgeBehaviour.LOOP:
                return 0

        return self.page_index + 1
