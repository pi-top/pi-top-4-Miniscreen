from pitop.common.sys_info import get_ssh_enabled_state

from ...actions import change_ssh_enabled_state
from ..templates.action import Page as ActionPage


class SSHActionPage(ActionPage):
    def __init__(self, size):
        super().__init__(
            size=size,
            get_state_method=get_ssh_enabled_state,
            set_state_method=change_ssh_enabled_state,
            icon="ssh",
            text="SSH",
        )
