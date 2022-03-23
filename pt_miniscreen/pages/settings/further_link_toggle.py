from pitop.common.sys_info import get_pt_further_link_enabled_state

from pt_miniscreen.actions import change_further_link_enabled_state
from pt_miniscreen.hotspots.action_page import ActionPage


class FurtherLinkTogglePage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Further Link",
            action=change_further_link_enabled_state,
            get_enabled_state=get_pt_further_link_enabled_state,
            **kwargs,
        )
