from pt_miniscreen.actions import (
    change_guacamole_enabled_state,
    get_guacamole_enabled_state,
)
from pt_miniscreen.components.action_page import ActionPage


class GuacamoleTogglePage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Guacamole",
            font_size=10,
            action=change_guacamole_enabled_state,
            get_enabled_state=get_guacamole_enabled_state,
            **kwargs,
        )
