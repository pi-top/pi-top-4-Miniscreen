from functools import partial
from time import sleep

import pytest

service_state = {
    "ssh": "Disabled",
    "further-link.service": "Disabled",
    "vncserver-x11-serviced.service": "Disabled",
}
ap_mode_status = {"state": "Inactive"}

initial_service_state = service_state.copy()
initial_ap_mode_status = ap_mode_status.copy()


def reset_status():
    global service_state
    global ap_mode_status
    service_state = initial_service_state.copy()
    ap_mode_status = initial_ap_mode_status.copy()


def start_service(service_to_enable):
    sleep(0.75)
    service_state[service_to_enable] = "Enabled"


def stop_service(service_to_disable):
    sleep(0.75)
    service_state[service_to_disable] = "Disabled"


def get_status(service):
    return service_state[service]


def get_ap_mode_status():
    return ap_mode_status


def change_wifi_mode():
    sleep(0.75)
    current_state = ap_mode_status["state"]
    ap_mode_status["state"] = "Inactive" if current_state == "Active" else "Active"


@pytest.fixture(autouse=True)
def setup(miniscreen, mocker):
    mocker.patch(
        "pt_miniscreen.actions.__enable_and_start_systemd_service", start_service
    )
    mocker.patch(
        "pt_miniscreen.actions.__disable_and_stop_systemd_service", stop_service
    )
    mocker.patch("pt_miniscreen.actions.get_systemd_enabled_state", get_status)
    mocker.patch("pt_miniscreen.actions.get_ap_mode_status", get_ap_mode_status)
    mocker.patch(
        "pt_miniscreen.pages.settings.ssh.get_ssh_enabled_state",
        partial(get_status, "ssh"),
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.vnc.get_vnc_enabled_state",
        partial(get_status, "vncserver-x11-serviced.service"),
    )
    mocker.patch(
        "pt_miniscreen.pages.settings.further_link.get_pt_further_link_enabled_state",
        partial(get_status, "further-link.service"),
    )
    mocker.patch("pt_miniscreen.pages.settings.ap.change_wifi_mode", change_wifi_mode)
    mocker.patch(
        "pt_miniscreen.pages.settings.hdmi_reset.reset_hdmi_configuration",
        lambda: sleep(1),
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

    yield

    reset_status()


def test_ssh(miniscreen, snapshot):
    # enable ssh
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable ssh
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_vnc(miniscreen, snapshot):
    # scroll down to vnc page
    miniscreen.down_button.release()
    sleep(1)

    # enable vnc
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable vnc
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "disabled.png")


def test_further_link(miniscreen, snapshot):
    # scroll down to further link page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    # enable further link
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable further link
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(1)
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
    snapshot.assert_match(miniscreen.device.display_image, "enabling.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enabled.png")

    # disable ap
    miniscreen.select_button.release()
    snapshot.assert_match(miniscreen.device.display_image, "disabling.png")
    sleep(1)
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
    miniscreen.select_button.release()
    sleep(0.1)
    snapshot.assert_match(miniscreen.device.display_image, "resetting.png")
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "reset.png")
