from time import sleep

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
            "pt_miniscreen.hotspots.cpu_bars.cpu_percent", return_value=cpu_percentages
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
    class SoftwarePageInfoMock:
        def __init__(self, os_version, run_number, sdk_version, pitopd_version, repos):
            self.os = f"pi-topOS {os_version}-{run_number}"
            self.sdk_version = f"SDK Version: {sdk_version}"
            self.pitopd_version = f"pi-topd Version: {pitopd_version}"
            self.repos = f"Repositories: {', '.join(repos)}"

    def set_software_page_mocks(
        os_version, run_number, sdk_version, pitopd_version, repos
    ):
        mocker.patch(
            "pt_miniscreen.pages.system.software.info",
            SoftwarePageInfoMock(
                os_version=os_version,
                run_number=run_number,
                sdk_version=sdk_version,
                pitopd_version=pitopd_version,
                repos=repos,
            ),
        )

    return set_software_page_mocks


@pytest.fixture
def pitop_hardware_page_mocks(mocker):
    class PtHardwarePageInfoMock:
        def __init__(self, fw_version, hw_version, pt_serial):
            self.fw_version = "Firmware Version: {fw_version}"
            self.hw_version = "Hardware Version: {hw_version}"
            self.pt_serial = "pi-top Serial Number: {pt_serial}"

    def set_pitop_hardware_page_mocks(fw_version, hw_version, pt_serial):
        mocker.patch(
            "pt_miniscreen.pages.system.pt_hardware.info",
            PtHardwarePageInfoMock(
                fw_version=fw_version, hw_version=hw_version, pt_serial=pt_serial
            ),
        )

    return set_pitop_hardware_page_mocks


@pytest.fixture
def rpi_hardware_page_mocks(mocker):
    class RPiHardwarePageInfoMock:
        def __init__(self, rpi_model, rpi_ram, rpi_serial):
            self.rpi_model: str = f"Model: {rpi_model}"
            self.rpi_ram: str = f"RAM: {rpi_ram}"
            self.rpi_serial: str = f"Serial Number: {rpi_serial}"

    def set_rpi_hardware_page_mocks(rpi_model, rpi_ram, rpi_serial):
        mocker.patch(
            "pt_miniscreen.pages.system.rpi_hardware.info",
            RPiHardwarePageInfoMock(
                rpi_model=rpi_model, rpi_ram=rpi_ram, rpi_serial=rpi_serial
            ),
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
        rpi_serial="1000000123123",
    )

    # enter system menu
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)


def test_login(miniscreen, snapshot, user):
    snapshot.assert_match(miniscreen.device.display_image, "default.png")

    user("olivier", default_pass=False)
    sleep(1.5)
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
    sleep(0.5)
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
    sleep(1.5)
    snapshot.assert_match(miniscreen.device.display_image, "memory-change.png")


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
