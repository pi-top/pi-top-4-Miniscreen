from pitop.common.sys_info import get_pt_further_link_enabled_state

from ...actions import change_further_link_enabled_state
from .action import Page as PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(
            interval=interval,
            size=size,
            mode=mode,
            config=config,
            get_state_method=get_pt_further_link_enabled_state,
            set_state_method=change_further_link_enabled_state,
            icon="further_link",
            text="Further Link",
        )
