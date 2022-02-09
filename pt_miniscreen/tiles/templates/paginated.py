import logging
from math import floor
from threading import Thread
from time import sleep

from PIL import Image

from pt_miniscreen.tiles.base import Tile

from ...event import AppEvent, post_event
from ...generators import scroll_to
from ...hotspots.base import HotspotInstance
from ...hotspots.scrollbar import Hotspot as ScrollbarHotspot
from ...hotspots.templates.rectangle import Hotspot as RectangleHotspot
from ...state import Speeds
from .viewport import ViewportTile

logger = logging.getLogger(__name__)


class PaginatedTile(Tile):
    SCROLL_PX_RESOLUTION = 2

    def __del__(self):
        super().__del__()

        for page in self.pages:
            page.cleanup()

    def __init__(self, size, pages, scrollbar_width=9, start_index=0, pos=(0, 0)):
        super().__init__(size=size, pos=pos)

        page_width = size[0] - scrollbar_width
        page_size = (page_width, size[1])
        self.pages = [Page(page_size) for Page in pages]
        self.page_index = start_index
        self.scrollbar_width = scrollbar_width
        scrollbar_border_width = 1

        self.pages_viewport = ViewportTile(
            size=page_size,
            pos=(self.scrollbar_width + scrollbar_border_width, 0),
            viewport_size=(page_width, size[1] * len(self.pages)),
            window_position=(0, page_size[1] * self.page_index),
        )

        # add pages to viewport
        for i, page in enumerate(self.pages):
            for hotspot_instance in page.hotspot_instances:
                xy = (
                    hotspot_instance.xy[0],
                    hotspot_instance.xy[1] + i * page.size[1],
                )
                self.pages_viewport.add_hotspot_instance(
                    HotspotInstance(hotspot_instance.hotspot, xy)
                )

        # add scrollbar
        bar_height = floor(size[1] / len(pages))
        self.scrollbar = ScrollbarHotspot(
            bar_height=bar_height,
            bar_y_start=start_index * bar_height,
            size=(scrollbar_width, size[1]),
            interval=0.01,
        )
        self.add_hotspot_instance(HotspotInstance(self.scrollbar, (0, 0)))

        # add right border for scrollbar
        self.add_hotspot_instance(
            HotspotInstance(
                RectangleHotspot(size=(scrollbar_border_width, size[1])),
                (scrollbar_width + 1, 0),
            )
        )

    def __setattr__(self, name, value) -> None:
        # Keep pages_viewport active property in sync with self.active
        if name == "active" and hasattr(self, "pages_viewport"):
            self.pages_viewport.active = value

        return super().__setattr__(name, value)

    @property
    def current_page(self):
        return self.pages[self.page_index]

    def needs_to_scroll(self) -> bool:
        final_y_pos = self.page_index * self.current_page.height
        return self.pages_viewport.y_pos != final_y_pos

    def update_scroll_position(self) -> None:
        if not self.needs_to_scroll():
            return

        try:
            value = next(self.scroll_coordinate_generator)
            self.pages_viewport.y_pos = value
            self.scrollbar.bar_y_pos = floor(
                (value * self.size[1] / self.pages_viewport._viewport_size[1])
            )
        except StopIteration:
            pass

    def scroll_to(self, index) -> bool:
        if self.needs_to_scroll() or index < 0 or index >= len(self.pages):
            return True

        previous_index = self.page_index
        self.page_index = index
        self.scroll_coordinate_generator = scroll_to(
            min_value=previous_index * self.size[1],
            max_value=self.page_index * self.size[1],  # sum of height of previous pages
            resolution=self.SCROLL_PX_RESOLUTION,
        )

        def scroll():
            while self.needs_to_scroll():
                self.update_scroll_position()
                post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)
                sleep(Speeds.SCROLL.value)

        Thread(target=scroll, daemon=True).start()
        return True

    def scroll_to_previous(self) -> bool:
        return self.scroll_to(self.page_index - 1)

    def scroll_to_next(self) -> bool:
        return self.scroll_to(self.page_index + 1)

    def handle_up_btn(self) -> bool:
        return self.scroll_to_previous()

    def handle_down_btn(self) -> bool:
        return self.scroll_to_next()

    # this seems to be the only way to compose tiles atm
    def get_preprocess_image(self):
        image = Image.new("1", self.size)
        image.paste(self.pages_viewport.image, self.pages_viewport.pos)
        return image
