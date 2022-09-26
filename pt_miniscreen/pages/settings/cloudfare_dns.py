from pt_miniscreen.actions import cloudfare_dns_is_set, toggle_cloudfare_dns
from pt_miniscreen.components.action_page import ActionPage


class CloudfareDnsPage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Cloudfare DNS",
            font_size=12,
            action=toggle_cloudfare_dns,
            get_enabled_state=cloudfare_dns_is_set,
            **kwargs,
        )
