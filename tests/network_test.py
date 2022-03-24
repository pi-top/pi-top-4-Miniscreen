from time import sleep

import pytest


@pytest.fixture
def internal_ip(mocker):
    return lambda page, interface, ip: mocker.patch(
        f"pt_miniscreen.pages.network.{page}.get_internal_ip",
        lambda iface: ip if interface == iface else "No IP address",
    )


@pytest.fixture(autouse=True)
def setup(miniscreen):
    # enter network menu
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)


def test_wifi(miniscreen, snapshot, internal_ip, mocker):
    snapshot.assert_match(miniscreen.device.display_image, "disconnected.png")

    internal_ip(page="wifi", interface="wlan0", ip="192.168.192.168")
    mocker.patch(
        "pt_miniscreen.pages.network.wifi.get_wifi_network_ssid",
        return_value="VM3409662",
    )
    mocker.patch(
        "pt_miniscreen.components.wifi_strength.get_network_strength",
        return_value="80%",
    )
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "connected.png")


def test_ethernet(miniscreen, snapshot, internal_ip):
    # scroll to ethernet page
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "disconnected.png")

    internal_ip(page="ethernet", interface="eth0", ip="10.255.10.255")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "connected.png")


def test_ap(miniscreen, snapshot, mocker):
    # scroll to ap page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "disconnected.png")

    mocker.patch(
        "pt_miniscreen.pages.network.ap.get_ap_mode_status",
        return_value={
            "ssid": "pitop1234",
            "passphrase": "12345678",
            "ip_address": "172.31.172.31",
        },
    )
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "connected.png")


def test_usb(miniscreen, snapshot, internal_ip):
    # scroll to usb page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "disconnected.png")

    internal_ip(page="usb", interface="ptusb0", ip="192.168.0.1")
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "connected.png")
