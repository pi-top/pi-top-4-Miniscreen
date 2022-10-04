from pt_miniscreen.actions import cloudflare_dns_is_set, toggle_cloudflare_dns
from pt_miniscreen.components.action_page import ActionPage


class CloudflareDnsPage(ActionPage):
    def __init__(self, **kwargs):
        super().__init__(
            text="Cloudflare DNS",
            font_size=9,
            action=toggle_cloudflare_dns,
            get_enabled_state=cloudflare_dns_is_set,
            **kwargs,
        )
