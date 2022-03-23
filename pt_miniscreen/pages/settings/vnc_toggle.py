from pitop.common.sys_info import get_vnc_enabled_state

from pt_miniscreen.actions import change_vnc_enabled_state
from pt_miniscreen.hotspots.action_page import ActionPage


class VNCTogglePage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="VNC",
            action=change_vnc_enabled_state,
            get_enabled_state=get_vnc_enabled_state,
            **kwargs,
        )
