import logging

from ...event import AppEvents, post_event
from ...generators import scroll_to
from ...hotspots.base import HotspotInstance
from .viewport import Tile as ViewportTile

logger = logging.getLogger(__name__)


class Tile(ViewportTile):
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, pos=(0, 0), pages=list()):
        assert len(pages) > 0
        super().__init__(
            size=size,
            pos=pos,
            viewport_size=(size[0], size[1] * len(pages)),
            window_position=(0, 0),
        )
        self.pages = pages

        self.page_index = 0

        hotspot_instances = list()
        for i, page in enumerate(self.pages):
            for hotspot_instance in page.hotspot_instances:
                xy = (hotspot_instance.xy[0], hotspot_instance.xy[1] + i * self.size[1])
                hotspot_instances.append(HotspotInstance(hotspot_instance.hotspot, xy))

        self.set_hotspot_instances(hotspot_instances, start=True)

    ###############################
    # Position - immediate/scroll #
    ###############################
    # Ignore scrolling behaviour
    def move_to_page_pos(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.height

    # Update scroll position if page is not to be moved to immediately
    @property
    def needs_to_scroll(self):
        final_y_pos = self.page_index * self._current_page.height
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
        new_menu = self._current_page.child_menu
        if not new_menu:
            return

        logger.info("Current menu's page has child menu - setting menu to child")

        for k, v in new_menu.items():
            self.menus[k] = v

        menu_tile_id = list(new_menu.keys())[0]
        post_event(AppEvents.GO_TO_CHILD_MENU, menu_tile_id)

    def go_to_parent_menu(self):
        post_event(AppEvents.GO_TO_PARENT_MENU)

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self):
        if self._current_page.child_menu:
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
        self._set_page_to_previous()
        if self.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    def handle_down_btn(self):
        self._set_page_to_next()
        if self.needs_to_scroll:
            post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

    ############
    # Internal #
    ############
    @property
    def _current_page(self):
        return self.pages[self.page_index]

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
            return self.page_index

        return self.page_index - 1

    def _get_next_page_index(self):
        if self.page_index == len(self.pages) - 1:
            return self.page_index

        return self.page_index + 1
