import logging

from ...event import AppEvent, post_event
from .paginated import PaginatedTile

logger = logging.getLogger(__name__)


class MenuTile(PaginatedTile):
    def handle_select_btn(self) -> bool:
        if self.current_page.child_menu_cls is not None:
            post_event(AppEvent.GO_TO_CHILD_MENU, self.current_page.child_menu_cls)
            return True

        elif hasattr(self.current_page, "action_state"):
            post_event(AppEvent.ACTION_START, self.current_page.start_action)
            return True

        return False
