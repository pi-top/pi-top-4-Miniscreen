import gc
import logging
from time import sleep
from unittest.mock import MagicMock
from weakref import ref

import pytest
from mocks.pitop import Miniscreen
from PIL import Image

from tests.mocks.pitop import Device

logger = logging.getLogger(__name__)


@pytest.fixture
def Root():
    from pt_miniscreen.core import Component

    class Root(Component):
        def __init__(self, on_rerender, **kwargs):
            super().__init__(**kwargs, on_rerender=on_rerender)
            self.on_rerender = on_rerender
            self._cleanup = MagicMock()
            self.render = MagicMock()

        # add dummy function for intervals
        def dummy(self):
            pass

    return Root


@pytest.fixture
def app(Root):
    from pt_miniscreen.core import App

    miniscreen = Miniscreen()
    miniscreen.device = MagicMock(spec=Device)()

    return App(miniscreen=miniscreen, Root=Root)


def test_creation(Root):
    from pt_miniscreen.core import App

    # raises exception when miniscreen is not passed
    try:
        App(Root=Root)
    except Exception as e:
        miniscreen_not_passed_error = e
    finally:
        assert str(miniscreen_not_passed_error) == ""

    # raises exception Root is not passed
    try:
        App(miniscreen=Miniscreen())
    except Exception as e:
        root_not_passed_error = e
    finally:
        assert str(root_not_passed_error) == ""

    # app created successfully when miniscreen and Root are passed
    app = App(miniscreen=Miniscreen(), Root=Root)

    # adds miniscreen and Root class as attributes
    assert hasattr(app, "miniscreen")
    assert hasattr(app, "Root")


def test_start(app):
    # does not initialise root component before being started
    assert not hasattr(app, "root")

    app.start()

    # creates root
    assert hasattr(app, "root")

    # calls render on root
    app.root.render.assert_called_once_with(Image.new("1", app.miniscreen.size))

    # calls miniscreen.device.display with render result
    app.miniscreen.device.display.assert_called_once_with(app.root.render())


def test_rerender(app):
    app.start()

    # reset render and display mocks
    app.root.render.reset_mock()
    app.miniscreen.device.display.reset_mock()

    app.root.on_rerender()

    # calls render on root
    app.root.render.assert_called_once_with(Image.new("1", app.miniscreen.size))

    # calls miniscreen.device.display with render result
    app.miniscreen.device.display.assert_called_once_with(app.root.render())


def test_stop(app):
    from pt_miniscreen.core import Component

    app.start()

    # create references to interval and child to check cleanup later
    root_child = ref(app.root.create_child(Component))
    root_interval = ref(app.root.create_interval(app.root.dummy))
    child_interval = ref(root_child().create_interval(root_child().cleanup))

    # root and it's children can be cleaned up after stop
    app.stop()
    gc.collect()
    assert app.root is None
    assert root_child() is None

    # intervals are cleaned up after their wait time elapses
    sleep(1)
    assert root_interval() is None
    assert child_interval() is None
