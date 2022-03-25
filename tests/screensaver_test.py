from time import sleep

import pytest

from conftest import setup_test


@pytest.fixture
def screensaver_app(mocker):
    setup_test(mocker, screensaver_timeout=0.2)
    from pt_miniscreen.app import App

    app = App()
    app.start()

    yield app

    app.stop()


@pytest.fixture(autouse=True)
def setup(mocker):
    # patch screensaver to display only one star in a fixed position
    mocker.patch(
        "pt_miniscreen.hotspots.starfield_screensaver.randrange",
        side_effect=lambda x, y: 1 if x == -25 else 10,
    )
    mocker.patch("pt_miniscreen.hotspots.starfield_screensaver.Hotspot.Z_MOVE", 0)


def test_screensaver(screensaver_app, snapshot):
    sleep(1)
    snapshot.assert_match(
        screensaver_app.miniscreen.device.display_image, "screensaver.png"
    )


def test_dim_state(screensaver_app, setup):
    sleep(0.3)
    assert screensaver_app.miniscreen._contrast == 0


def test_miniscreen_default_contrast(app):
    assert app.miniscreen._contrast == 255
