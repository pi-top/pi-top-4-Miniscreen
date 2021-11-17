import logging
import time

from PIL import Image

from .config import ConfigFactory
from .config.classes.menu_edge_behaviour import MenuEdgeBehaviour
from .hotspots.base import HotspotInstance
from .scroll import scroll_generator
from .viewport import Viewport

logger = logging.getLogger(__name__)


class Menu:
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, mode, redraw_speed, config):
        self.mode = mode
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

        self.viewport = Viewport(
            window_size=self.size,
            display_size=self.display_size,
            mode=self.mode,
        )

        self.setup_hotspot_position_in_viewport()

    # Adjust each hotspot's xy to match position in viewport
    def setup_hotspot_position_in_viewport(self):
        self.viewport.remove_all_hotspots()
        for i, page in enumerate(self.pages):
            for upperleft_xy, hotspots in page.hotspots.items():
                for hotspot in hotspots:
                    pos = (
                        int(upperleft_xy[0]),
                        int(upperleft_xy[1] + i * self.window_height),
                    )
                    self.viewport.add_hotspot(
                        HotspotInstance(hotspot, pos), collection_id=page
                    )

    def resize_pages(self):
        for page in self.pages:
            page.size = self.size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        logger.debug(f"Resizing menu from {self._size} to {value}")
        self._size = value

        # Resize viewport
        self.viewport.stop_threads()
        # self.viewport.size = self.display_size
        # self.viewport.window_size = self.size
        logger.error(f"menu.size setter - {self.size}")

        self.viewport = Viewport(
            window_size=self.size,
            display_size=self.display_size,
            mode=self.mode,
        )

        # Resize hotspots and update their positions
        self.resize_pages()
        self.setup_hotspot_position_in_viewport()

    @property
    def window_width(self):
        return self.size[0]

    @window_width.setter
    def window_width(self, value):
        self.size = (value, self.window_height)

    @property
    def window_height(self):
        return self.size[1]

    @window_height.setter
    def window_height(self, value):
        self.size = (self.window_width, value)

    @property
    def display_size(self):
        return (self.window_width, self.window_height * len(self.config.children))

    @property
    def current_page(self):
        return self.pages[self.page_index]

    @property
    def y_pos(self):
        return self.viewport._position[1]

    @y_pos.setter
    def y_pos(self, pos):
        self.viewport.position = (0, pos)

    def move_to_page(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.viewport.height

    @property
    def image(self):
        start = time.time()

        im = Image.new(self.current_page.mode, self.current_page.size)
        logger.debug(f"Menu Image size: {im.size}")

        viewport_image = self.viewport.image
        if viewport_image is None:
            viewport_image = Image.new(self.current_page.mode, self.current_page.size)
        im.paste(viewport_image, (0, 0) + self.current_page.size)

        end = time.time()
        logger.debug(f"Time generating image: {end - start}")

        return im

    def set_page_index_to(self, page_index):
        if self.page_index == page_index:
            return
        self.page_index = page_index
        self.scroll_coordinate_generator = scroll_generator(
            min_value=self.y_pos,
            max_value=self.page_index * self.viewport.window_height,
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
