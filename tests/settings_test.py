from functools import partial
from time import sleep
from typing import Dict

import pytest


class SettingsState:
    def __init__(self) -> None:
        self.service_state: Dict = {}
        self.ap_mode_status: Dict = {}
        self.reset_status()

    def reset_status(self):
        for service in (
            "ssh",
            "further-link.service",
            "vncserver-x11-serviced.service",
        ):
            self.service_state[service] = "Disabled"
        self.ap_mode_status["state"] = "Inactive"

    def start_service(self, service_to_enable):
        sleep(1)
        self.service_state[service_to_enable] = "Enabled"

    def stop_service(self, service_to_disable):
        sleep(1)
        self.service_state[service_to_disable] = "Disabled"

    def get_status(self, service):
        return self.service_state[service]

    def get_ap_mode_status(self):
        return self.ap_mode_status

    def change_wifi_mode(self):
        sleep(1)
        current_state = self.ap_mode_status["state"]
        self.ap_mode_status["state"] = (
            "Inactive" if current_state == "Active" else "Active"
        )

    def reset_hdmi_configuration(self):
        sleep(1)


@pytest.fixture(autouse=True)
def setup(miniscreen, mocker):
    settings_manager = SettingsState()
    mocker.patch(
        "pt_miniscreen.actions.__enable_and_start_systemd_service",
        settings_manager.start_service,
    )
    mocker.patch(
        "pt_miniscreen.actions.__disable_and_stop_systemd_service",
        settings_manager.stop_service,
    )
    mocker.patch(
        "pt_miniscreen.actions.get_systemd_enabled_state", settings_manager.get_status
    )
    mocker.patch(
        "pt_miniscreen.actions.get_ap_mode_status", settings_manager.get_ap_mode_status
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.ssh.get_ssh_enabled_state",
        partial(settings_manager.get_status, "ssh"),
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.vnc.get_vnc_enabled_state",
        partial(settings_manager.get_status, "vncserver-x11-serviced.service"),
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.further_link.get_pt_further_link_enabled_state",
        partial(settings_manager.get_status, "further-link.service"),
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.ap.change_wifi_mode",
        settings_manager.change_wifi_mode,
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.hdmi_reset.reset_hdmi_configuration",
        settings_manager.reset_hdmi_configuration,
    )

    # enter settings menu
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)


def test_ssh(miniscreen, snapshot):
    # enable ssh
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable ssh
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_vnc(miniscreen, snapshot):
    # scroll down to vnc page
    miniscreen.down_button.release()
    sleep(1)

    # enable vnc
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable vnc
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_further_link(miniscreen, snapshot):
    # scroll down to further link page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    # enable further link
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable further link
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_ap(miniscreen, snapshot):
    # scroll down to ap page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    # enable ap
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable ap
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_hdmi_reset(miniscreen, snapshot):
    # scroll down to screen reset
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    # reset screen
    snapshot.assert_match(miniscreen.device.display_image, "reset.png")

    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "resetting.png")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "reset.png")
