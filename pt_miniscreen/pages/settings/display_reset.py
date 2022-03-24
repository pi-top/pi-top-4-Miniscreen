from pt_miniscreen.actions import reset_hdmi_configuration
from pt_miniscreen.components.action_page import ActionPage


class DisplayResetPage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Reset Display",
            action=reset_hdmi_configuration,
            **kwargs,
        )
