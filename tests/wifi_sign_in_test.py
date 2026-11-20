from time import sleep

import pytest

from conftest import setup_app

HOTSPOT = {"state": "Active", "ssid": "pi-top-7FF2", "passphrase": "4u4szauo"}


@pytest.fixture
def portal(mocker):
    state = {"portal": False, "hotspot": {}}
    mocker.patch(
        "pt_miniscreen.network_status.get_connectivity",
        side_effect=lambda check_now=False: "portal" if state["portal"] else "full",
    )
    mocker.patch(
        "pt_miniscreen.pages.root.wifi_sign_in.get_ap_mode_status",
        side_effect=lambda: state["hotspot"],
    )
    run = mocker.patch("pt_miniscreen.pages.root.wifi_sign_in.run_command")
    yield state, run

    from pt_miniscreen import network_status

    network_status._last["portal"] = False


@pytest.fixture
def miniscreen(mocker, portal):
    setup_app(mocker)

    from pt_miniscreen.app import App

    mocker.patch.object(App, "WIFI_SIGN_IN_POLL", 0.5)
    mocker.patch.object(App, "WIFI_SIGNED_IN_SECONDS", 1)
    app = App()
    app.start()
    yield app.miniscreen
    app.stop()


def test_wifi_sign_in_popup(miniscreen, portal, snapshot):
    state, run = portal

    state["portal"] = True
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "step-1.png")

    miniscreen.select_button.release()
    state["hotspot"] = HOTSPOT
    sleep(3)
    snapshot.assert_match(miniscreen.device.display_image, "step-2.png")
    run.assert_any_call("/usr/bin/wifi-ap-sta start", timeout=30)

    state["portal"] = False
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "signed-in.png")
    run.assert_any_call("/usr/bin/wifi-ap-sta stop", timeout=30)

    sleep(4)
    snapshot.assert_match(miniscreen.device.display_image, "closed.png")


def test_wifi_sign_in_popup_closes_and_reopens_with_o(miniscreen, portal, snapshot):
    state, _ = portal

    state["portal"] = True
    sleep(2)
    miniscreen.cancel_button.release()
    sleep(4)
    snapshot.assert_match(miniscreen.device.display_image, "closed.png")

    miniscreen.select_button.release()
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "reopened.png")


def test_wifi_page_offers_the_sign_in(miniscreen, portal, snapshot):
    state, _ = portal

    state["portal"] = True
    sleep(2)
    miniscreen.cancel_button.release()
    sleep(2)

    # Network menu, then its first page: Wi-Fi
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "wifi-page.png")

    miniscreen.select_button.release()
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "opened-from-wifi-page.png")


@pytest.fixture
def app_with_short_timeouts(mocker, portal):
    setup_app(mocker, screensaver_timeout=1)

    from pt_miniscreen.app import App

    mocker.patch.object(App, "WIFI_SIGN_IN_POLL", 0.5)
    app = App()
    app.start()
    yield app
    app.stop()


def test_popup_keeps_the_screen_awake(app_with_short_timeouts, portal, mocker):
    app = app_with_short_timeouts
    state, _ = portal

    state["portal"] = True
    sleep(4)
    assert app.root.showing_wifi_sign_in
    assert not app.dimmed
    assert not app.root.is_screensaver_running

    # only for a while
    mocker.patch.object(app, "WIFI_SIGN_IN_KEEP_AWAKE", 0)
    sleep(3)
    assert app.dimmed or app.root.is_screensaver_running
