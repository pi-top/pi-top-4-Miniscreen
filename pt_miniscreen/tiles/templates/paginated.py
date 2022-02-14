import logging
from threading import Thread
from time import sleep

from ...event import AppEvent, post_event
from ...generators import scroll_to
from ...hotspots.base import HotspotInstance
from ...state import Speeds
from .viewport import ViewportTile

logger = logging.getLogger(__name__)


class PaginatedTile(ViewportTile):
    SCROLL_PX_RESOLUTION = 2

    def __init__(self, size, pages, start_index=0, pos=(0, 0)):
        self.pages = pages
        self.page_index = start_index

        super().__init__(
            size=size,
            pos=pos,
            viewport_size=(size[0], size[1] * len(self.pages)),
            window_position=(0, size[1] * self.page_index),
        )

        hotspot_instances = list()
        for i, page in enumerate(self.pages):
            for hotspot_instance in page.hotspot_instances:
                xy = (hotspot_instance.xy[0], hotspot_instance.xy[1] + i * self.size[1])
                hotspot_instances.append(HotspotInstance(hotspot_instance.hotspot, xy))

        self.set_hotspot_instances(hotspot_instances)

    @property
    def current_page(self):
        return self.pages[self.page_index]

    def needs_to_scroll(self) -> bool:
        final_y_pos = self.page_index * self.current_page.height
        return self.y_pos != final_y_pos

    def update_scroll_position(self) -> None:
        if not self.needs_to_scroll():
            return

        try:
            value = next(self.scroll_coordinate_generator)
            self.y_pos = value
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
