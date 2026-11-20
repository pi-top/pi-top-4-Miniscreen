import logging
from threading import Thread

from pitop.common.command_runner import run_command
from pitop.common.sys_info import get_ap_mode_status

from pt_miniscreen.components.mixins import Actionable, HasGutterIcons
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)

FONT_SIZE = 10

# set when the popup turned the hotspot on, so it's turned off again after sign-in
_hotspot_started = {"value": False}


def get_hotspot():
    status = get_ap_mode_status()
    if status.get("state", "").lower() == "active" and status.get("ssid"):
        return status
    return None


def start_hotspot():
    _hotspot_started["value"] = True
    try:
        run_command("/usr/bin/wifi-ap-sta start", timeout=30)
    except Exception as e:
        logger.error(f"Couldn't start the hotspot: {e}")


def stop_hotspot_if_started():
    if not _hotspot_started["value"]:
        return
    _hotspot_started["value"] = False
    try:
        run_command("/usr/bin/wifi-ap-sta stop", timeout=30)
        run_command("/usr/bin/wifi-ap-sta disable", timeout=30)
    except Exception as e:
        logger.error(f"Couldn't stop the hotspot: {e}")


def get_popup_text(hotspot, signed_in, starting=False):
    if signed_in:
        return "Wi-Fi signed in"
    if hotspot:
        return "\n".join(
            [
                "2. On your device",
                f"join {hotspot['ssid']}",
                f"pw {hotspot.get('passphrase', '')}",
                "and sign in",
            ]
        )
    if starting:
        return "Starting hotspot"
    return "Wi-Fi sign-in:\n1. Press O to\nturn on hotspot"


class WifiSignInPopup(Component, Actionable, HasGutterIcons):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            initial_state={
                "hotspot": get_hotspot(),
                "signed_in": False,
                "starting": False,
            },
        )
        self.text = self.create_child(
            Text,
            text=get_popup_text(self.state["hotspot"], False),
            font_size=FONT_SIZE,
            align="center",
            vertical_align="center",
            spacing=2,
            wrap=False,
        )
        # the hotspot's name and password appear a few seconds after starting it
        self.create_interval(self.refresh_hotspot, 2)

    def refresh_hotspot(self):
        self.state.update({"hotspot": get_hotspot()})

    def on_state_change(self, previous_state):
        self.text.state.update(
            {
                "text": get_popup_text(
                    self.state["hotspot"],
                    self.state["signed_in"],
                    self.state["starting"],
                )
            }
        )

    def show_signed_in(self):
        self.state.update({"signed_in": True})

    def perform_action(self):
        if self.state["hotspot"] or self.state["signed_in"] or self.state["starting"]:
            return
        self.state.update({"starting": True})
        Thread(target=self._start_hotspot, daemon=True).start()

    def _start_hotspot(self):
        start_hotspot()
        self.state.update({"starting": False, "hotspot": get_hotspot()})

    def top_gutter_icon(self):
        return None

    def bottom_gutter_icon(self):
        if self.state["hotspot"] or self.state["signed_in"] or self.state["starting"]:
            return None
        return get_image_file_path("gutter/tick.png")

    def render(self, image):
        return self.text.render(image)
