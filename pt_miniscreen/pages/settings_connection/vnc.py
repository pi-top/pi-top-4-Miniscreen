from pitop.common.sys_info import get_vnc_enabled_state

from ...actions import change_vnc_enabled_state
from ..templates.action import Page as ActionPage


class VNCActionPage(ActionPage):
    def __init__(self, size):
        super().__init__(
            size=size,
            get_state_method=get_vnc_enabled_state,
            set_state_method=change_vnc_enabled_state,
            icon="vnc",
            text="VNC",
        )
