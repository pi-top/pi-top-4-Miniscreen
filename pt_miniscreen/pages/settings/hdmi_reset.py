from pt_miniscreen.hotspots.action_page import ActionPage

from ...actions import reset_hdmi_configuration


class HDMIResetPage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Reset Display",
            action=reset_hdmi_configuration,
            **kwargs,
        )
