from time import sleep

import pytest

from conftest import setup_app


@pytest.fixture
def screensaver_app(mocker):
    setup_app(mocker, screensaver_timeout=0.2)

    from pt_miniscreen.app import App

    app = App()
    app.start()

    yield app

    app.stop()


@pytest.fixture(autouse=True)
def setup(mocker):
    # patch screensaver to display only one star in a fixed position
    mocker.patch(
        "pt_miniscreen.pages.root.screensaver.randrange",
        side_effect=lambda x, y: 10 if x == 1 else 1,
    )
    mocker.patch("pt_miniscreen.pages.root.screensaver.Star.DELTA_Z", 0)


def test_screensaver(screensaver_app, snapshot):
    sleep(1)
    snapshot.assert_match(
        screensaver_app.miniscreen.device.display_image, "screensaver.png"
    )


def test_dim_state(screensaver_app, setup):
    sleep(0.3)
    assert screensaver_app.miniscreen._contrast == 0
