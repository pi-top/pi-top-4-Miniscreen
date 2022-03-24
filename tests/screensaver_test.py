from time import sleep

import pytest


@pytest.fixture(autouse=True)
def mock_timeouts(mocker):
    from pt_miniscreen.state import State, timeouts

    timeouts[State.DIM] = 0.1
    timeouts[State.SCREENSAVER] = 0.5


@pytest.fixture(autouse=True)
def setup(mocker):
    # patch screensaver to display only one star in a fixed position
    mocker.patch(
        "pt_miniscreen.hotspots.starfield_screensaver.randrange",
        side_effect=lambda x, y: 1 if x == -25 else 10,
    )
    mocker.patch("pt_miniscreen.hotspots.starfield_screensaver.Hotspot.Z_MOVE", 0)


def test_screensaver(miniscreen, snapshot):
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "screensaver.png")


def test_dim_state(app):
    sleep(0.4)
    from pt_miniscreen.state import State

    assert app.state_manager._state == State.DIM
