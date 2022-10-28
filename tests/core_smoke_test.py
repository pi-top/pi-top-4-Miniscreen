import logging
from functools import partial
from time import sleep

import pytest

from .mocks.pitop import Miniscreen

logger = logging.getLogger(__name__)


@pytest.fixture
def Counter():
    from pt_miniscreen.core import Component
    from pt_miniscreen.core.components import Text

    class Counter(Component):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, initial_state={"count": 0})
            self.count_text = self.create_child(
                Text, text="0", align="center", vertical_align="center"
            )

        def on_state_change(self, previous_state):
            if previous_state["count"] != self.state["count"]:
                self.count_text.state.update({"text": str(self.state["count"])})

        def render(self, image):
            return self.count_text.render(image)

    return Counter


@pytest.fixture
def Timer(Counter):
    from pt_miniscreen.core import Component

    class Timer(Component):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.counter = self.create_child(Counter)
            self.increment_interval = self.create_interval(self.increment_count)

        def increment_count(self):
            self.counter.state.update({"count": self.counter.state["count"] + 1})

        def render(self, image):
            return self.counter.render(image)

    return Timer


@pytest.fixture
def Root(Counter, Timer):
    from pt_miniscreen.core import Component
    from pt_miniscreen.core.components import List, Row, Text

    Title = partial(Text, font_size=12, align="center", vertical_align="center")

    class Root(Component):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.list = self.create_child(
                List,
                Rows=[
                    partial(
                        Row,
                        column_widths=["auto", "auto"],
                        Columns=[partial(Title, text="Counter"), Counter],
                    ),
                    partial(
                        Row,
                        column_widths=["auto", "auto"],
                        Columns=[partial(Title, text="Timer"), Timer],
                    ),
                ],
            )

        def render(self, image):
            return self.list.render(image)

    return Root


def test_smoke(snapshot, Root):
    from pt_miniscreen.core import App

    miniscreen = Miniscreen()

    app = App(miniscreen.device.display, Root)

    # does not update display before being started
    assert miniscreen.device.display_image == b""

    app.start()

    # update display
    snapshot.assert_match(miniscreen.device.display_image, "started.png")

    # get counter out of list rows
    counter = app.root.list.rows[0].columns[1]

    # shows nested component updates syncronously
    counter.state.update({"count": 1})
    snapshot.assert_match(miniscreen.device.display_image, "update.png")

    # shows updates from an interval
    sleep(1.1)
    snapshot.assert_match(miniscreen.device.display_image, "interval-update.png")

    # does not show changes when stopped
    app.stop()
    counter.state.update({"count": 1})
    sleep(1.1)
    snapshot.assert_match(miniscreen.device.display_image, "stopped.png")

    # can start app again
    app.start()
    snapshot.assert_match(miniscreen.device.display_image, "started-again.png")
