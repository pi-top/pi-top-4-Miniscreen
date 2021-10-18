from .base import Page
from .battery import Page as BatteryPage

# CarryOnPage,
# ConnectPitopWifiNetworkPage,
# GetDevicePage,
# HelpURLPage,
# OpenBrowserPage,
# StartWirelessConnectionPage,
# WelcomePage,


class PageFactory:
    pages = {
        Page.BATTERY: BatteryPage,
        # Page.WELCOME: WelcomePage,
        # Page.START_WIRELESS_CONNECTION: StartWirelessConnectionPage,
        # Page.HELP_URL: HelpURLPage,
        # Page.GET_DEVICE: GetDevicePage,
        # Page.CONNECT_PITOP_WIFI_NETWORK: ConnectPitopWifiNetworkPage,
        # Page.OPEN_BROWSER: OpenBrowserPage,
        # Page.CARRY_ON: CarryOnPage,
    }

    @staticmethod
    def get_page(page_type: Page):
        return PageFactory.pages[page_type]
