import logging
from itertools import repeat
from time import sleep
import pytest

from conftest import use_test_font, use_test_images

logger = logging.getLogger(__name__)


def freeze_marquee_text(mocker):
    def carousel(end, start=0, step=1):
        return repeat(start)

    mocker.patch("pt_miniscreen.core.components.marquee_text.carousel", carousel)


def global_setup(mocker):
    use_test_images(mocker)
    use_test_font(mocker, "pt_miniscreen.utils")
    use_test_font(mocker, "pt_miniscreen.core.components.text")


def setup_welcome_app(mocker):
    global_setup(mocker)
    freeze_marquee_text(mocker)


@pytest.fixture
def welcome_app(mocker):
    setup_welcome_app(mocker)

    from pt_miniscreen.welcome.app import WelcomeApp

    app = WelcomeApp()
    app.start()

    yield app

    app.stop()


@pytest.fixture
def miniscreen(welcome_app):
    yield welcome_app.miniscreen


def test_app_flows(miniscreen, snapshot):
    snapshot.assert_match(miniscreen.device.display_image, "first_page.png")

    # Up button press is ignored
    miniscreen.up_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "first_page.png")

    # Down button press is ignored
    miniscreen.down_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "first_page.png")

    # Cancel button press is ignored
    miniscreen.cancel_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "first_page.png")

    # Select button press shows next page
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "second_page.png")

    # Up button press is ignored
    miniscreen.up_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "second_page.png")

    # Down button press is ignored
    miniscreen.down_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "second_page.png")

    # Select button press is ignored
    miniscreen.select_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "second_page.png")

    # Cancel button press closes the app
    miniscreen.cancel_button.release()
    sleep(0.5)
    snapshot.assert_match(miniscreen.device.display_image, "empty.png")
