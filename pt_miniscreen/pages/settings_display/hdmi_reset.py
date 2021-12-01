from ...actions import reset_hdmi_configuration
from ..templates.action import Page as ActionPage


class HDMIResetPage(ActionPage):
    def __init__(self, size):
        super().__init__(
            size=size,
            get_state_method=None,
            set_state_method=reset_hdmi_configuration,
            icon="hdmi_reset",
            text="Reset Display",
        )
