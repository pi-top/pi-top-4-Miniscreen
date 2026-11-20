def test_is_updating_follows_the_update_monitor_hold_file(mocker, tmp_path):
    from pt_miniscreen import update_status

    hold_file = tmp_path / "reboot-guard.conf"
    mocker.patch.object(update_status, "UPDATE_HOLD_FILE", str(hold_file))
    assert not update_status.is_updating()

    hold_file.write_text("[Unit]\nRefuseManualStart=yes\n")
    assert update_status.is_updating()
