def test_miniscreen_fixture(miniscreen):
    # test buttons work
    released = {
        "cancel": False,
        "select": False,
        "up": False,
        "down": False,
    }

    def when_cancel_button_released():
        released["cancel"] = True

    def when_select_button_released():
        released["select"] = True

    def when_up_button_released():
        released["up"] = True

    def when_down_button_released():
        released["down"] = True

    miniscreen.cancel_button.when_released = when_cancel_button_released
    miniscreen.select_button.when_released = when_select_button_released
    miniscreen.up_button.when_released = when_up_button_released
    miniscreen.down_button.when_released = when_down_button_released

    miniscreen.cancel_button.release()
    miniscreen.select_button.release()
    miniscreen.up_button.release()
    miniscreen.down_button.release()

    assert released["cancel"]
    assert released["select"]
    assert released["up"]
    assert released["down"]

    # test default values
    assert miniscreen.size == (128, 64)
    assert not miniscreen.is_active
