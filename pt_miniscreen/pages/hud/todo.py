from subprocess import run

from ..base import PageBase
from ..event import AppEvents, subscribe


class WelcomePage(PageBase):
    """That's it!

    Now press DOWN to scroll...
    """

    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.text = "That's it!\nNow press DOWN to scroll..."


class StartWirelessConnectionPage(PageBase):
    """Awesome!

    Press DOWN to continue through pi-top connection setup...
    """

    def __init__(self, interval, size, mode):
        super().__init__(
            interval=interval,
            size=size,
            mode=mode,
        )
        self.text = "Awesome! Press DOWN to continue through pi-top connection setup..."


class HelpURLPage(PageBase):
    """Detailed setup instructions: pi-top.com/start-4.

    Press SELECT to continue
    """

    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.text = "Detailed setup instructions: pi-top.com/start-4"


class GetDevicePage(PageBase):
    """Let's get started!

    You will need a laptop/computer to connect with...
    """

    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.text = (
            "Let's get started!\nYou will need a\nlaptop/computer\nto connect with..."
        )
        self.wrap = False


class ConnectPitopWifiNetworkPage(PageBase):
    """Connect to Wi-Fi network '{ssid}' using password '{passphrase}'."""

    def __init__(self, interval, size, mode):
        super().__init__(
            interval=interval,
            size=size,
            mode=mode,
        )
        self.font_size = 13
        self.wrap = False

        self.ssid = ""

        def update_ssid(ssid):
            self.ssid = ssid

        subscribe(AppEvents.AP_HAS_SSID, update_ssid)

        self.passphrase = ""

        def update_passphrase(passphrase):
            self.passphrase = passphrase

        subscribe(AppEvents.AP_HAS_PASSPHRASE, update_passphrase)

    @property
    def text(self):
        return f"Connect to\nWi-Fi network:\n'{self.ssid}'\n'{self.passphrase}'"


class OpenBrowserPage(PageBase):
    # Default: "Waiting for connection...", then:
    """Open browser to http://pi-top.local or http://192.168.64.1."""

    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.wrap = False

        self.has_connected_device = False

        def update_has_connected_device(has_connected_device):
            self.has_connected_device = has_connected_device

        subscribe(AppEvents.HAS_CONNECTED_DEVICE, update_has_connected_device)

        self.is_connected_to_internet = False

        def update_is_connected(is_connected):
            self.is_connected_to_internet = is_connected

        subscribe(AppEvents.IS_CONNECTED_TO_INTERNET, update_is_connected)

    # TODO: cycle through alternative IP addresses (e.g. Ethernet)
    # ip -4 addr [show eth0] | grep --only-matching --perl-regexp '(?<=inet\s)\d+(\.\d+){3}' | grep --invert-match 127.0.0.1

    # ip -4 addr  | grep -oP '(?<=inet\s)\d+(\.\d+){3}'

    # Refresh before each pass of IP addresses?
    # Refresh before showing an IP address in the list?

    # Try and get IP from eth0, use that
    # Try and get IP from wlan0, use that
    # Else AP/display cable IP

    @property
    def text(self):
        txt = "Waiting for\nconnection..."

        if self.has_connected_device or self.is_connected_to_internet:
            hostname = run("hostname", encoding="utf-8", capture_output=True)
            hostname = hostname.stdout.strip()
            txt = f"Open browser to\nhttp://{hostname}.local\nor\nhttp://192.168.64.1"

        return txt


class CarryOnPage(PageBase):
    """You've started the onboarding!

    Continue in your browser...
    """

    def __init__(self, interval, size, mode):
        super().__init__(interval=interval, size=size, mode=mode)
        self.text = "You've started the onboarding!\nContinue in your browser..."
        self.visible = False

        def update_visible(visible):
            self.visible = visible

        subscribe(AppEvents.READY_TO_BE_A_MAKER, update_visible)
