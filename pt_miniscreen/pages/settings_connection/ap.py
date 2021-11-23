from ...actions import change_wifi_mode, get_wifi_ap_state
from ..templates.action import Page as ActionPage


class Page(ActionPage):
    def __init__(self, size):
        super().__init__(
            size=size,
            get_state_method=get_wifi_ap_state,
            set_state_method=change_wifi_mode,
            # TODO: use correct icon
            icon="ssh",
            text="Access Point",
        )
