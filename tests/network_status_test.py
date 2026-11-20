import pytest


@pytest.fixture
def run_command(mocker):
    return mocker.patch("pt_miniscreen.network_status.run_command")


def test_reads_the_last_result(run_command):
    from pt_miniscreen.network_status import get_connectivity, needs_sign_in

    run_command.return_value = "portal\n"

    assert get_connectivity() == "portal"
    assert needs_sign_in() is True
    run_command.assert_called_with(
        "nmcli -t -f CONNECTIVITY general", timeout=15, log_errors=False
    )


def test_check_now_asks_for_a_new_check(run_command):
    from pt_miniscreen.network_status import needs_sign_in

    run_command.return_value = "full\n"

    assert needs_sign_in(check_now=True) is False
    run_command.assert_called_with(
        "nmcli networking connectivity check", timeout=15, log_errors=False
    )


def test_remembers_the_last_result_for_pages(run_command):
    from pt_miniscreen.network_status import is_behind_portal, needs_sign_in

    run_command.return_value = "portal\n"
    needs_sign_in()
    assert is_behind_portal() is True

    run_command.return_value = "full\n"
    needs_sign_in()
    assert is_behind_portal() is False


def test_unknown_when_nmcli_fails(run_command):
    from pt_miniscreen.network_status import get_connectivity, needs_sign_in

    run_command.side_effect = Exception("no nmcli")

    assert get_connectivity() == "unknown"
    assert needs_sign_in() is False


HOTSPOT = {"state": "Active", "ssid": "pi-top-7FF2", "passphrase": "4u4szauo"}


def test_popup_text():
    from pt_miniscreen.pages.root.wifi_sign_in import get_popup_text

    assert get_popup_text(None, False).splitlines() == [
        "Wi-Fi sign-in:",
        "1. Press O to",
        "turn on hotspot",
    ]
    assert get_popup_text(None, False, starting=True) == "Starting hotspot"
    assert get_popup_text(HOTSPOT, False).splitlines() == [
        "2. On your device",
        "join pi-top-7FF2",
        "pw 4u4szauo",
        "and sign in",
    ]
    assert get_popup_text(HOTSPOT, True) == "Wi-Fi signed in"


def test_hotspot_is_stopped_only_if_the_popup_started_it(mocker):
    from pt_miniscreen.pages.root import wifi_sign_in

    run = mocker.patch.object(wifi_sign_in, "run_command")

    wifi_sign_in.stop_hotspot_if_started()
    run.assert_not_called()

    wifi_sign_in.start_hotspot()
    wifi_sign_in.stop_hotspot_if_started()
    wifi_sign_in.stop_hotspot_if_started()
    assert [c.args[0] for c in run.call_args_list] == [
        "/usr/bin/wifi-ap-sta start",
        "/usr/bin/wifi-ap-sta stop",
        "/usr/bin/wifi-ap-sta disable",
    ]
