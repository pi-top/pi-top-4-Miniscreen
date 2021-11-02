from ...actions import reset_hdmi_configuration
from .action import Page as PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config, offset):
        super().__init__(
            interval=interval,
            size=size,
            mode=mode,
            config=config,
            set_state_method=reset_hdmi_configuration,
            icon="hdmi_reset",
            offset=offset,
        )
