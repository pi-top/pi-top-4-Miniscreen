import logging
from time import sleep

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup(mocker):
    mocker.patch("pt_miniscreen.pages.system.login.getuser", return_value="root")
    mocker.patch(
        "pt_miniscreen.pages.system.login.is_pi_using_default_password",
        return_value=True,
    )


def test_hud_navigation(miniscreen, snapshot):
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")

    miniscreen.down_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "system.png")

    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enter-system.png")

    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "leave-system.png")

    miniscreen.down_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "network.png")

    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enter-network.png")

    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "leave-network.png")

    miniscreen.down_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "projects.png")

    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enter-projects.png")

    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "leave-projects.png")

    miniscreen.down_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "settings.png")

    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "enter-settings.png")

    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "leave-settings.png")

    miniscreen.up_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "scroll-up.png")


def test_hud_navigation_on_cancel_button_press(miniscreen, snapshot):
    def press_cancel_button_and_wait():
        miniscreen.cancel_button.release()
        sleep(2)

    def scroll_to_distance(distance):
        for _ in range(distance):
            miniscreen.down_button.release()
            sleep(1)

    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")

    scroll_to_distance(distance=1)
    snapshot.assert_match(miniscreen.device.display_image, "system.png")

    press_cancel_button_and_wait()
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")

    scroll_to_distance(distance=2)
    snapshot.assert_match(miniscreen.device.display_image, "network.png")

    press_cancel_button_and_wait()
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")

    scroll_to_distance(distance=3)
    snapshot.assert_match(miniscreen.device.display_image, "projects.png")

    press_cancel_button_and_wait()
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")

    scroll_to_distance(distance=4)
    snapshot.assert_match(miniscreen.device.display_image, "settings.png")

    press_cancel_button_and_wait()
    snapshot.assert_match(miniscreen.device.display_image, "overview.png")
