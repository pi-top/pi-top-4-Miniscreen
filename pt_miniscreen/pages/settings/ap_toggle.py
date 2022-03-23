from pt_miniscreen.actions import change_wifi_mode, get_wifi_ap_state
from pt_miniscreen.hotspots.action_page import ActionPage


class APTogglePage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Wi-Fi Hotspot",
            font_size=13,
            action=change_wifi_mode,
            get_enabled_state=get_wifi_ap_state,
            **kwargs,
        )
