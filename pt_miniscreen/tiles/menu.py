import logging

from ..config import ConfigFactory
from ..config.classes.menu_edge_behaviour import MenuEdgeBehaviour
from ..generators import scroll_to
from ..hotspots.base import HotspotInstance
from ..tiles import ViewportTile

logger = logging.getLogger(__name__)


class MenuTile(ViewportTile):
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, mode, redraw_speed, config):
        super().__init__(
            display_size=lambda: self.size,
            tile_size=lambda: self.tile_size,
            mode=mode,
        )
        self.mode = mode
        self.tile_size = size
        self._size = size
        self.redraw_speed = redraw_speed
        self.page_index = 0
        self.config = config

        self.parent_goes_to_first_page = config.parent_goes_to_first_page
        self.top_edge = config.top_edge
        self.bottom_edge = config.bottom_edge
        self.title_bar = config.title_bar

        config_factory = ConfigFactory(self.size, self.mode, self.redraw_speed)

        self.pages = list()
        for page_name, page_config in self.config.children.items():
            self.pages.append(config_factory.get(page_config))

        self.add_page_hotspots_into_viewport()

    def add_page_hotspots_into_viewport(self):
        self.remove_all_hotspots()
        for i, page in enumerate(self.pages):
            for upperleft_xy, hotspots in page.hotspots.items():
                for hotspot in hotspots:
                    pos = (
                        int(upperleft_xy[0]),
                        int(upperleft_xy[1] + i * self.window_height),
                    )
                    self.add_hotspot(HotspotInstance(hotspot, pos), collection_id=page)

    def resize_pages(self):
        for page in self.pages:
            page.size = self.size

    @property
    def display_size(self):
        return (self.window_width, self.window_height * len(self.config.children))

    @property
    def current_page(self):
        return self.pages[self.page_index]

    def move_to_page(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.height

    def set_page_index_to(self, page_index):
        if self.page_index == page_index:
            return
        self.page_index = page_index
        self.scroll_coordinate_generator = scroll_to(
            min_value=self.y_pos,
            max_value=self.page_index * self.window_height,
            resolution=self.SCROLL_PX_RESOLUTION,
        )

    def set_page_to_previous(self):
        if self.needs_to_scroll:
            return

        previous_index = self.page_index
        self.set_page_index_to(self.get_previous_page_index())
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    def set_page_to_next(self):
        if self.needs_to_scroll:
            return

        previous_index = self.page_index
        self.set_page_index_to(self.get_next_page_index())
        logger.debug(f"Page index: {previous_index} -> {self.page_index}")

    def get_previous_page_index(self):
        if self.page_index == 0:
            if self.top_edge == MenuEdgeBehaviour.NONE:
                return self.page_index

            elif self.top_edge == MenuEdgeBehaviour.BOUNCE:
                return self.get_next_page_index()

            elif self.top_edge == MenuEdgeBehaviour.LOOP:
                return len(self.pages) - 1

        return self.page_index - 1

    def get_next_page_index(self):
        if self.page_index == len(self.pages) - 1:
            if self.bottom_edge == MenuEdgeBehaviour.NONE:
                return self.page_index

            elif self.bottom_edge == MenuEdgeBehaviour.BOUNCE:
                return self.get_previous_page_index()

            elif self.bottom_edge == MenuEdgeBehaviour.LOOP:
                return 0

        return self.page_index + 1

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
