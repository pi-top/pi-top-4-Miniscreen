import logging

from conftest import setup_app

logger = logging.getLogger(__name__)


def test_broken_pipe_error(mocker):
    setup_app(mocker)

    from pt_miniscreen.app import App

    app = App()
    app.start()

    # app displays correctly after being started
    assert app.miniscreen.device.display_image is not None

    # raise BrokenPipeError
    mocker.patch.object(app, "_display", side_effect=BrokenPipeError())
    app.display()

    # app root and timers are None because app has been stopped so process can end
    assert app.root is None
    assert app.dimming_timer is None
    assert app.screensaver_timer is None
