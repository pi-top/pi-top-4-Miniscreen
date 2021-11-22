from pitop.common.sys_info import get_pt_further_link_enabled_state

from ...actions import change_further_link_enabled_state
from ..templates.action import Page as ActionPage


class Page(ActionPage):
    def __init__(self, size, mode, config):
        super().__init__(
            size=size,
            mode=mode,
            config=config,
            get_state_method=get_pt_further_link_enabled_state,
            set_state_method=change_further_link_enabled_state,
            icon="further_link",
            text="Further Link",
        )
