from ...actions import reset_hdmi_configuration
from ..templates.action import Page as ActionPage


class Page(ActionPage):
    def __init__(self, size, mode):
        super().__init__(
            size=size,
            mode=mode,
            get_state_method=None,
            set_state_method=reset_hdmi_configuration,
            icon="hdmi_reset",
            text="Reset Display",
        )
