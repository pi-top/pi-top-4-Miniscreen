from time import sleep

import pytest


@pytest.fixture
def battery():
    from pt_miniscreen.pages.hud.overview import battery

    yield battery

    battery.reset()


@pytest.fixture
def internal_ip(mocker):
    def patch(_interface, ip=""):
        mocker.patch(
            "pt_miniscreen.pages.hud.overview.get_internal_ip",
            lambda interface: ip if interface == _interface else "None",
        )
        mocker.patch(
            "pt_miniscreen.pages.hud.overview.is_url", lambda url: url == f"http://{ip}"
        )

    return patch


def test_overview_battery(battery, miniscreen, snapshot):
    battery.is_charging = True
    battery.when_charging()
    sleep(1.5)
    snapshot.assert_match(miniscreen.device.display_image, "charging.png")

    battery.is_full = True
    battery.capacity = 100
    battery.when_full()
    sleep(1.5)
    snapshot.assert_match(miniscreen.device.display_image, "full.png")

    battery.is_charging = False
    battery.is_full = False
    battery.capacity = 99
    battery.when_discharging()
    sleep(1.5)
    snapshot.assert_match(miniscreen.device.display_image, "discharging.png")

    battery.capacity = 98
    battery.on_capacity_change(98)
    sleep(1.5)
    snapshot.assert_match(miniscreen.device.display_image, "capacity-change.png")


def test_overview_network(miniscreen, snapshot, internal_ip):
    internal_ip("wlan0", "192.168.192.168")
    sleep(4.5)
    snapshot.assert_match(miniscreen.device.display_image, "wifi.png")

    internal_ip("eth0", "10.255.10.255")
    sleep(4.5)
    snapshot.assert_match(miniscreen.device.display_image, "ethernet.png")

    internal_ip("ptusb0", "172.31.172.31")
    sleep(4.5)
    snapshot.assert_match(miniscreen.device.display_image, "usb.png")

    internal_ip("lo", "127.0.0.1")
    sleep(4.5)
    snapshot.assert_match(miniscreen.device.display_image, "localhost.png")
