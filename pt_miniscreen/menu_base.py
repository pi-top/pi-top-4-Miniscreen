import logging

from .config_factory import ConfigFactory
from .viewport import Viewport

logger = logging.getLogger(__name__)


class MenuBase:
    def __init__(self, size, mode, redraw_speed, config, overlay_render_func=None):

        self.go_to_first = config.go_to_first

        self.pages = []
        menu_factory = ConfigFactory(size, mode, redraw_speed)
        for name, config in config.children.items():
            self.pages.append(menu_factory.get(config))

        self.page_index = 0

        self.viewport = Viewport(
            display_size=(size[0], size[1] * len(self.pages)),
            window_size=size,
            mode=mode,
        )

        self.overlay_render_func = overlay_render_func

        for i, page in enumerate(self.pages):
            self.viewport.add_hotspot(page, (0, i * size[1]))

    @property
    def current_page(self):
        return self.pages[self.page_index]

    @property
    def y_pos(self):
        return self.viewport._position[1]

    @y_pos.setter
    def y_pos(self, pos):
        return self.viewport.set_position((0, pos))

    def move_to_page(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.viewport.height

    @property
    def image(self):
        im = self.viewport.image.copy()

        if callable(self.overlay_render_func):
            self.overlay_render_func(im)

        return im

    def set_page_index_to(self, page_index):
        self.page_index = page_index

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
        # Return next page if at top
        if self.page_index == 0:
            return self.get_next_page_index()

        idx = self.page_index - 1
        candidate = self.pages[idx]
        return idx if candidate.visible else self.page_index

    def get_next_page_index(self):
        # Return current page if at end
        if self.page_index + 1 >= len(self.pages):
            return self.page_index

        idx = self.page_index + 1
        candidate = self.pages[idx]
        return idx if candidate.visible else self.page_index

    @property
    def needs_to_scroll(self):
        correct_y_pos = self.page_index * self.current_page.height
        return self.y_pos != correct_y_pos
