import gc
import logging
from multiprocessing import Event
from threading import Thread
from time import sleep
from unittest.mock import patch
from weakref import ref

import pytest
from PIL import Image

from pt_miniscreen.core.component import RenderException

logger = logging.getLogger(__name__)


def create_spot_image(pos, size=(128, 64)):
    image = Image.new("1", size)
    image.putpixel(pos, 1)
    return image


@pytest.fixture
def SpotComponent():
    from pt_miniscreen.core import Component

    class Spot(Component):
        default_state = {"spot_pos": (0, 0)}

        def move_spot_right(self):
            current_pos = self.state["spot_pos"]
            self.state.update({"spot_pos": (current_pos[0] + 1, current_pos[1])})

        def move_spot_down(self):
            current_pos = self.state["spot_pos"]
            self.state.update({"spot_pos": (current_pos[0], current_pos[1] + 1)})

        def render(self, image):
            image.putpixel(self.state["spot_pos"], 1)
            return image

    return Spot


def test_creation(parent):
    from pt_miniscreen.core import Component

    # raises exception when created without on_rerender
    try:
        Component()
    except Exception as e:
        creation_error = e
    finally:
        assert (
            str(creation_error)
            == "Component must be created with create_child method. This error might be because kwargs not passed to super in component init method."
        )

    # raises exception when on_rerender is not a bound method
    try:
        Component(on_rerender=lambda: None)
    except Exception as e:
        bound_method_error = e
    finally:
        assert (
            str(bound_method_error)
            == "argument should be a bound method, not <class 'function'>"
        )

    # can be created successfully when on_rerender is a bound method
    Component(on_rerender=parent._reconcile)

    # can be created successfully when `create_child` is used
    component = parent.create_child(Component)
    assert isinstance(component, Component)

    # creates state object
    assert hasattr(component, "state")


def test_updates_during_creation(parent, SpotComponent):
    from pt_miniscreen.core import Component

    class MovingSpot(SpotComponent):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.state.update({"spot_pos": (1, 1)})

    class Spots(Component):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.spot_one = self.create_child(MovingSpot)
            self.spot_two = self.create_child(MovingSpot)

        def render(self, image):
            image = self.spot_one.render(image)
            return self.spot_two.render(image)

    # creating component tree that updates during creation does not error
    parent.create_child(Spots)


def test_render(parent, SpotComponent):
    component = parent.create_child(SpotComponent)

    # returns expected output
    expected_output = create_spot_image((0, 0))
    render_output = component.render(Image.new("1", (128, 64)))
    assert render_output == expected_output

    # returns cached image instead rendering when input is unchanged
    with patch.object(component, "_original_render", return_value=expected_output):
        render_output = component.render(Image.new("1", (128, 64)))
        assert render_output == expected_output
        component._original_render.assert_not_called()

    # bypasses cache when when input image changes
    expected_output = create_spot_image((0, 0), size=(80, 40))
    render_output = component.render(Image.new("1", (80, 40)))
    assert render_output == expected_output


def test_state(parent):
    from pt_miniscreen.core import Component

    component = parent.create_child(
        Component, initial_state={"foo": "bar", "deep": {"foo": "bar"}}
    )

    # state is a dictionary
    assert isinstance(component.state, dict)

    # state cannot be assigned to
    try:
        component.state = None
    except AttributeError as e:
        assert (
            str(e)
            == "Component.state cannot be set, pass initial_state to super().__init__ or call self.state.update"
        )
    finally:
        assert component.state is not None

    # state has same equality behaviour as a normal dict
    assert component.state == {"foo": "bar", "deep": {"foo": "bar"}}

    # state has same string represenation as a normal dict
    assert str(component.state) == "{'foo': 'bar', 'deep': {'foo': 'bar'}}"

    # state can be changed using update method
    component.state.update({"new": "state"})
    assert component.state == {"new": "state", "foo": "bar", "deep": {"foo": "bar"}}

    # state can be changed by assigning
    component.state["foo"] = "BAR"
    assert component.state["foo"] == "BAR"


def test_on_state_change(mocker, parent):
    from pt_miniscreen.core import Component

    component = parent.create_child(Component, initial_state={"foo": "bar"})
    mocker.patch.object(component, "on_state_change")

    # does not call on_state_change when update does not change state
    component.state.update({"foo": "bar"})
    component.on_state_change.assert_not_called()

    # calls on_state_change with previous state when update changes state
    component.state.update({"foo": "BAR"})
    component.on_state_change.assert_called_with({"foo": "bar"})
    component.on_state_change.reset_mock()

    # calls on_state_change with previous state when update adds state
    component.state.update({"new": "state"})
    component.on_state_change.assert_called_with({"foo": "BAR"})


def test_rerendering(parent, SpotComponent):
    component = parent.create_child(SpotComponent)

    # on_rerender method not called if state does not change
    component.state.update({"spot_pos": (0, 0)})
    parent.on_rerender_spy.assert_not_called()

    # on_rerender method not called if state is changed before initial render
    component.state.update({"foo": "bar"})
    parent.on_rerender_spy.assert_not_called()

    # trigger initial render
    component.render(Image.new("1", (128, 64)))

    # on_rerender method not called if update does not result in new output
    component.state.update({"new": "state"})
    parent.on_rerender_spy.assert_not_called()

    # on_rerender method not called if state is changed by assignment
    component.state["foo"] = "BAR"
    parent.on_rerender_spy.assert_not_called()

    # on_rerender method called if update results in new output
    component.state.update({"spot_pos": (1, 1)})
    parent.on_rerender_spy.assert_called_once()
    parent.on_rerender_spy.reset_mock()

    # updates made on a removed child do not call on_rerender method
    parent.remove_child(component)
    component.state.update({"spot_pos": (2, 2)})
    parent.on_rerender_spy.assert_not_called()


def test_concurrent_reconciliation(parent, SpotComponent):
    component = parent.create_child(SpotComponent)

    # trigger initial render so state changes cause reconciliation
    component.render(Image.new("1", (128, 64)))

    # acquire reconciliation lock to simulate an update being in-progress
    component._reconciliation_lock.acquire()

    # state update does not cause rerender while lock is acquired
    Thread(target=component.state.update, args=[{"spot_pos": (1, 1)}]).start()
    sleep(0.1)
    parent.on_rerender_spy.assert_not_called()

    # subsequent updates also do not cause rerender
    Thread(target=component.state.update, args=[{"spot_pos": (2, 2)}]).start()
    sleep(0.1)
    parent.on_rerender_spy.assert_not_called()

    # when lock released only a single rerender triggered by previous updates
    component._reconciliation_lock.release()
    sleep(0.1)
    parent.on_rerender_spy.assert_called_once()


def test_intervals(parent, SpotComponent, render):
    from pt_miniscreen.core.component import Interval

    component = parent.create_child(SpotComponent)

    # render so component becomes active
    render(parent)

    # returns an Interval instance
    move_right_interval = component.create_interval(component.move_spot_right)
    assert isinstance(move_right_interval, Interval)

    # does not call method when interval is created
    output = component.render(Image.new("1", (128, 64)))
    assert output != create_spot_image((1, 0))

    # calls method after a second by default
    sleep(1.05)
    output = component.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((1, 0))

    # can use custom interval time
    move_down_interval = component.create_interval(component.move_spot_down, 0.5)
    sleep(0.55)
    output = component.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((1, 1))

    # both intervals are active at once
    sleep(0.55)
    output = component.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((2, 2))

    # cancelling intervals stops them calling their method again
    move_down_interval.cancel()

    # after a second only move_spot_down should have been called
    sleep(1.05)
    output = component.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((3, 2))

    # calling `remove_interval` also stops the interval
    component.remove_interval(move_right_interval)

    # after a second spot should not have moved
    sleep(1.05)
    output = component.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((3, 2))


def test_pausing(parent, SpotComponent):
    from pt_miniscreen.core.component import Component

    class MovingRightSpot(SpotComponent):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.create_interval(self.move_spot_right)

    class MovingDownSpot(SpotComponent):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.create_interval(self.move_spot_down)

    class Spots(Component):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs, initial_state={"spot_attribute": "moving_right_spot"}
            )
            self.moving_right_spot = self.create_child(MovingRightSpot)
            self.moving_down_spot = self.create_child(MovingDownSpot)

        def render(self, image):
            return getattr(self, self.state["spot_attribute"]).render(image)

    spots = parent.create_child(Spots)

    # when parent not rendered child active event should not be set
    assert not spots.moving_right_spot.active_event.is_set()
    assert not spots.moving_down_spot.active_event.is_set()

    # when not active intervals should not run
    sleep(1.05)
    output = spots.moving_right_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((0, 0))
    output = spots.moving_down_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((0, 0))

    # when parent rendered only children that were rendered should be active
    parent.render(Image.new("1", (128, 64)))
    assert spots.moving_right_spot.active_event.is_set()
    assert not spots.moving_down_spot.active_event.is_set()

    # only active children have their intervals run
    sleep(1.05)
    output = spots.moving_right_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((1, 0))
    output = spots.moving_down_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((0, 0))

    # when an update hides or shows a component their active state is updated
    spots.state.update({"spot_attribute": "moving_down_spot"})
    assert not spots.moving_right_spot.active_event.is_set()
    assert spots.moving_down_spot.active_event.is_set()

    # when pausing a component the interval runs once more
    sleep(1.05)
    output = spots.moving_right_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((2, 0))

    # newly active components also run their intervals
    output = spots.moving_down_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((0, 1))

    # paused components don't run their interval another time
    sleep(1.05)
    output = spots.moving_right_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((2, 0))
    output = spots.moving_down_spot.render(Image.new("1", (128, 64)))
    assert output == create_spot_image((0, 2))


def test_render_exceptions(parent, SpotComponent, render):
    from pt_miniscreen.core import Component

    class NoReturn(Component):
        def render(self, image):
            pass

    class ModifyImageSize(Component):
        def render(self, image):
            return image.crop((0, 0, 10, 10))

    # attempting to render a component without a render method raises error
    try:
        render(parent.create_child(Component))
    except NotImplementedError as e:
        render_not_implemented_error = e
    finally:
        assert (
            str(render_not_implemented_error)
            == "Component subclasses must implement the render method"
        )

    try:
        render(parent.create_child(NoReturn))
    except RenderException as e:
        no_return_exception = e
    finally:
        assert (
            str(no_return_exception)
            == "Pillow Image must be returned from render, returned None"
        )

    try:
        render(parent.create_child(SpotComponent), size=(0, 64))
    except RenderException as e:
        no_width_exception = e
    finally:
        assert (
            str(no_width_exception)
            == "Image passed to render must have non-zero height and width"
        )

    try:
        render(parent.create_child(SpotComponent), size=(128, 0))
    except RenderException as e:
        no_height_exception = e
    finally:
        assert (
            str(no_height_exception)
            == "Image passed to render must have non-zero height and width"
        )

    try:
        render(parent.create_child(ModifyImageSize))
    except RenderException as e:
        image_size_change_exception = e
    finally:
        assert (
            str(image_size_change_exception)
            == "Image returned from render must be same size as the passed image: passed (128, 64), returned (10, 10)"
        )


def test_removing_unknown_interval(mocker, parent):
    from pt_miniscreen.core import Component

    component = parent.create_child(Component)

    # create interval that component does not own and spy on it's cancel method
    unknown_interval = parent.create_interval(parent.dummy)
    mocker.patch.object(unknown_interval, "cancel")

    # try to remove unknown interval
    component.remove_interval(unknown_interval)

    # interval should not have been cancelled
    unknown_interval.cancel.assert_not_called()


def test_removing_unknown_child(mocker, parent):
    from pt_miniscreen.core import Component

    component = parent.create_child(Component)

    # create child that component does not own and spy on it's cleanup method
    unknown_child = parent.create_child(Component)
    mocker.patch.object(unknown_child, "cleanup")

    # try to remove unknown child
    component.remove_child(unknown_child)

    # child should not have been cleaned up
    unknown_child.cleanup.assert_not_called()


def test_remove_active_child_cleanup(parent, SpotComponent, render):
    # store created objects in refs so we don't create references to them
    component = ref(parent.create_child(SpotComponent))
    child = ref(component().create_child(SpotComponent))
    interval = ref(component().create_interval(component().move_spot_right))

    # render parent so children are active
    render(parent)

    # removing child calls cleanup method
    with patch.object(component(), "cleanup"):
        parent.remove_child(component())
        component().cleanup.assert_called_once()

    # component can be garbage collected after being removed
    gc.collect()
    assert component() is None

    # component children are also garbage collected
    assert child() is None

    # after a second the interval stops and is collected
    sleep(1.1)
    assert interval() is None


def test_remove_paused_child_cleanup(parent, SpotComponent, render):
    # store created objects in refs so we don't create references to them
    component = ref(parent.create_child(SpotComponent))
    child = ref(component().create_child(SpotComponent))
    interval = ref(component().create_interval(component().move_spot_right))

    # removing child calls cleanup method
    with patch.object(component(), "cleanup"):
        parent.remove_child(component())
        component().cleanup.assert_called_once()

    # component can be garbage collected after being removed
    gc.collect()
    assert component() is None

    # component children are also garbage collected
    assert child() is None

    # after a second the interval stops and is collected
    sleep(1.1)
    assert interval() is None


def test_no_references_active_component_cleanup():
    from pt_miniscreen.core import Component

    # use event rather than spy so reference count not influenced
    # event is easier than boolean due to scope issues
    cleanup_called = Event()

    class Parentless(Component):
        def __init__(self):
            super().__init__(self.dummy)

        def cleanup(self):
            logger.debug("cleanup called")
            cleanup_called.set()

        # add a dummy method to use for on_rerender and interval
        def dummy(self):
            pass

    component = Parentless()
    child = ref(component.create_child(Component))
    interval = ref(component.create_interval(component.dummy))

    # set component active
    component._set_active(True)

    # component cleanup method is called when it is garbage collected
    del component
    gc.collect()
    assert cleanup_called.is_set()

    # component children are also garbage collected
    assert child() is None

    # after about a second the interval stops and is collected
    sleep(1.1)
    assert interval() is None


def test_no_references_paused_component_cleanup():
    from pt_miniscreen.core import Component

    # use event rather than spy so reference count not influenced
    # event is easier than boolean due to scope issues
    cleanup_called = Event()

    class Parentless(Component):
        def __init__(self):
            super().__init__(self.dummy)

        def cleanup(self):
            logger.debug("cleanup called")
            cleanup_called.set()

        # add a dummy method to use for on_rerender and interval
        def dummy(self):
            pass

    component = Parentless()
    child = ref(component.create_child(Component))
    interval = ref(component.create_interval(component.dummy))

    # pause component
    component._set_active(False)

    # component cleanup method is called when it is garbage collected
    del component
    gc.collect()
    assert cleanup_called.is_set()

    # component children are also garbage collected
    assert child() is None

    # after about a second the interval stops and is collected
    sleep(1.1)
    assert interval() is None
