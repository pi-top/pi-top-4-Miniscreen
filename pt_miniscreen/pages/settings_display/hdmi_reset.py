from ...actions import reset_hdmi_configuration
from ..templates.action import Page as ActionPage


class Page(ActionPage):
    def __init__(self, interval, size, mode, config):
        super().__init__(
            interval=interval,
            size=size,
            mode=mode,
            config=config,
            get_state_method=None,
            set_state_method=reset_hdmi_configuration,
            icon="hdmi_reset",
            text="Reset Display",
        )
