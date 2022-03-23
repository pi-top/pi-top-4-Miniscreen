from pitop.common.sys_info import get_ssh_enabled_state

from pt_miniscreen.hotspots.action_page import ActionPage

from ...actions import change_ssh_enabled_state


class SSHActionPage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="SSH",
            action=change_ssh_enabled_state,
            get_enabled_state=get_ssh_enabled_state,
            **kwargs,
        )
