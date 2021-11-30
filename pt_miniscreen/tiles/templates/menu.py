import logging
from time import sleep

from ...event import AppEvent, post_event
from ...hotspots.base import HotspotInstance
from ...state import Speeds
from .viewport import ViewportTile

logger = logging.getLogger(__name__)


class MenuTile(ViewportTile):
    def __init__(self, menu_cls, size, pos=(0, 0)):
        self.menu = menu_cls(size)

        super().__init__(
            size=size,
            pos=pos,
            viewport_size=(size[0], size[1] * len(self.menu.pages)),
            window_position=(0, 0),
        )

        hotspot_instances = list()
        for i, page in enumerate(self.menu.pages):
            for hotspot_instance in page.hotspot_instances:
                xy = (hotspot_instance.xy[0], hotspot_instance.xy[1] + i * self.size[1])
                hotspot_instances.append(HotspotInstance(hotspot_instance.hotspot, xy))

        self.set_hotspot_instances(hotspot_instances, start=True)

    @property
    def image(self):
        self.update_scroll_position()
        return super().image

    ##################################
    # Button Press API (when active) #
    ##################################
    def handle_select_btn(self) -> bool:
        if self.menu.has_child_menu:
            self.menu.go_to_child_menu()
            return True
        # elif False:
        #     post_event(AppEvent.BUTTON_ACTION_START)
        #     return True
        return False

    def handle_cancel_btn(self) -> bool:
        return False

    def handle_up_btn(self) -> bool:
        if self.needs_to_scroll:
            return True

        self.menu.set_page_to_previous()

        self.emit_image_update_events_until_finished_scrolling()

        return True

    def handle_down_btn(self) -> bool:
        if self.needs_to_scroll:
            return True

        self.menu.set_page_to_next()

        self.emit_image_update_events_until_finished_scrolling()

        return True

    def emit_image_update_events_until_finished_scrolling(self):
        while self.needs_to_scroll:
            post_event(AppEvent.UPDATE_DISPLAYED_IMAGE)
            sleep(Speeds.SCROLL.value)

    # Update scroll position if page is not to be moved to immediately
    @property
    def needs_to_scroll(self) -> bool:
        final_y_pos = self.menu.page_index * self.menu.current_page.height
        return self.y_pos != final_y_pos

    def update_scroll_position(self) -> None:
        if not self.needs_to_scroll:
            return

        try:
            value = next(self.menu.scroll_coordinate_generator)
            self.y_pos = value
        except StopIteration:
            pass
