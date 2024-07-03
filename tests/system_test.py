from time import sleep
from unittest.mock import Mock

import pytest


@pytest.fixture
def user(mocker):
    def set_user(user, default_pass):
        mocker.patch("pt_miniscreen.pages.system.login.getuser", return_value=user)
        mocker.patch(
            "pt_miniscreen.pages.system.login.is_pi_using_default_password",
            return_value=default_pass,
        )

    return set_user


@pytest.fixture
def battery():
    from pt_miniscreen.pages.system.battery import battery

    yield battery

    battery.reset()


@pytest.fixture
def cpu_percent(mocker):
    def set_cpu_percent(cpu_percentages, interval=1):
        mocker.patch(
            "pt_miniscreen.components.cpu_bars.cpu_percent",
            return_value=cpu_percentages,
        )

    return set_cpu_percent


@pytest.fixture
def memory(mocker):
    # patch bytes2human and fudge to use MB to make numbers easier
    def bytes2human(mb):
        return "%.2fMB" % mb

    mocker.patch("pt_miniscreen.pages.system.memory.bytes2human", bytes2human)

    # return function to set virtual and swap levels
    class MockMemoryStats:
        def __init__(self, total, used):
            self.total = total
            self.used = used
            self.percent = used * 100 / total

    def set_memory(virtual, swap):
        mocker.patch(
            "pt_miniscreen.pages.system.memory.psutil.virtual_memory",
            return_value=MockMemoryStats(total=999, used=virtual),
        )
        mocker.patch(
            "pt_miniscreen.pages.system.memory.psutil.swap_memory",
            return_value=MockMemoryStats(total=500, used=swap),
        )

    return set_memory


@pytest.fixture
def software_page_mocks(mocker):
    def set_software_page_mocks(
        os_version, run_number, sdk_version, pitopd_version, repos
    ):
        def get_package_version_mock(package_name):
            if package_name == "python3-pitop":
                return sdk_version
            elif package_name == "pi-topd":
                return pitopd_version

        def get_apt_repositories_mock():
            return repos

        class OsInfoMock:
            build_os_version = os_version
            build_run_number = run_number

        mocker.patch(
            "pt_miniscreen.pages.system.software.get_pitopOS_info",
            return_value=OsInfoMock,
        )
        mocker.patch(
            "pt_miniscreen.pages.system.software.get_package_version",
            get_package_version_mock,
        )
        mocker.patch(
            "pt_miniscreen.pages.system.software.get_apt_repositories",
            get_apt_repositories_mock,
        )

    return set_software_page_mocks


@pytest.fixture
def pitop_hardware_page_mocks(mocker):
    def set_pitop_hardware_page_mocks(fw_version, hw_version, pt_serial):
        class FirmwareDeviceMock:
            def get_fw_version():
                return fw_version

            def get_sch_hardware_version_major():
                return hw_version

        mocker.patch(
            "pt_miniscreen.pages.system.pt_hardware.FirmwareDevice",
            return_value=FirmwareDeviceMock,
        )
        mocker.patch(
            "pt_miniscreen.pages.system.pt_hardware.get_pt_serial",
            return_value=pt_serial,
        )

    return set_pitop_hardware_page_mocks


@pytest.fixture
def rpi_hardware_page_mocks(mocker):
    def set_rpi_hardware_page_mocks(rpi_model, rpi_ram, rpi_serial):
        mocker.patch(
            "pt_miniscreen.pages.system.rpi_hardware.rpi_model", return_value=rpi_model
        )
        mocker.patch(
            "pt_miniscreen.pages.system.rpi_hardware.rpi_ram", return_value=rpi_ram
        )
        mocker.patch(
            "pt_miniscreen.pages.system.rpi_hardware.rpi_serial",
            return_value=rpi_serial,
        )

    return set_rpi_hardware_page_mocks


@pytest.fixture(autouse=True)
def setup(
    miniscreen,
    cpu_percent,
    user,
    memory,
    software_page_mocks,
    pitop_hardware_page_mocks,
    rpi_hardware_page_mocks,
):
    # setup default mock values
    cpu_percent([90, 10, 20, 50])
    user("root", default_pass=True)
    memory(virtual=500, swap=100)
    software_page_mocks(
        sdk_version="0.8.1-2",
        pitopd_version="13.4.4-0",
        os_version="3.0",
        run_number="322",
        repos=["pi-top-os", "pi-top-os-testing"],
    )
    pitop_hardware_page_mocks(fw_version="5.4", hw_version="8", pt_serial="5219233")
    rpi_hardware_page_mocks(
        rpi_model="Raspberry Pi 4 Model B Rev 1.2",
        rpi_ram="3.7 GB",
        rpi_serial="98798777",
    )

    # enter system menu
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)


def test_login(miniscreen, snapshot, user):
    snapshot.assert_match(miniscreen.device.display_image, "default.png")

    user("olivier", default_pass=False)
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "custom.png")


def test_battery(battery, miniscreen, snapshot):
    # scroll to battery page
    miniscreen.down_button.release()
    sleep(1)

    battery.is_charging = True
    battery.when_charging()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "charging.png")

    battery.is_full = True
    battery.capacity = 100
    battery.when_full()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "full.png")

    battery.is_charging = False
    battery.is_full = False
    battery.capacity = 99
    battery.when_discharging()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "discharging.png")

    battery.capacity = 98
    battery.on_capacity_change(98)
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "capacity-change.png")


def test_cpu(miniscreen, snapshot, cpu_percent):
    # scroll to cpu page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "default.png")

    cpu_percent([55.5, 30, 10, 100])
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "levels-change.png")


def test_memory(miniscreen, snapshot, memory):
    # scroll to memory page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "default.png")

    memory(virtual=999, swap=127.9876655)
    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "memory-change.png")


def test_updates(miniscreen, snapshot, mocker):
    run_command_mock = Mock(return_value="....")
    mocker.patch("pt_miniscreen.pages.system.last_update.run_command", run_command_mock)

    has_fw_updates_mock = Mock(return_value=False)
    mocker.patch(
        "pt_miniscreen.pages.system.last_update._has_fw_updates", has_fw_updates_mock
    )

    last_update_date_mock = Mock(return_value=False)
    mocker.patch(
        "pt_miniscreen.pages.system.last_update._get_last_update_breadcrumb_mtime",
        last_update_date_mock,
    )

    # scroll to updates page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "on_enter.png")

    # Set breadcrumb date
    last_update_date_mock.return_value = "2024-07-02 12:50"

    # System updates are now available
    run_command_mock.return_value = """
Listing... Done
pt-os-web-portal-desktop/bullseye 0.20.2-1 all [upgradable from: 0.20.2-1]
pt-os-web-portal/bullseye 0.20.2-1 all [upgradable from: 0.20.2-1]"""

    # Firmware updates are now available
    has_fw_updates_mock.return_value = True

    sleep(2)
    snapshot.assert_match(miniscreen.device.display_image, "updates_available.png")

    # Fail to check for last update breadcrumb date
    last_update_date_mock.return_value = None
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no_latest_date.png")

    # No system updates available
    run_command_mock.return_value = ""
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no_system_updates.png")

    # No firwmare updates available
    has_fw_updates_mock.return_value = False
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no_fw_updates.png")


def test_software(miniscreen, snapshot):
    # scroll to software page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "software.png")


def test_pitop_hardware(miniscreen, snapshot):
    # scroll to pi-top hardware page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "pt_hardware.png")


def test_rpi_hardware(miniscreen, snapshot):
    # scroll to raspberry pi hardware page
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)

    snapshot.assert_match(miniscreen.device.display_image, "rpi_hardware.png")
