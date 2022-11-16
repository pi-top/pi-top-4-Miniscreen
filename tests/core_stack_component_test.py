import gc
import logging
import sys
from functools import partial
from math import ceil
from time import sleep
from weakref import ref

import pytest
from PIL import Image

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@pytest.fixture
def create_stack(create_component):
    from pt_miniscreen.core.components import Stack

    return partial(create_component, Stack)


@pytest.fixture
def ImagePage(get_test_image_path):
    from pt_miniscreen.core.components import Image as ImageComponent

    class ImagePage(ImageComponent):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs,
                image_path=get_test_image_path("test-1.png"),
                resize=True,
                resize_resampling=Image.Resampling.BOX,
            )

    return ImagePage


@pytest.fixture
def CheckeredPage():
    from pt_miniscreen.core import Component
    from pt_miniscreen.core.utils import checkered

    class Checkered(Component):
        def render(self, image):
            return checkered(image)

    return Checkered


def test_initial_stack(create_stack, render, ImagePage, CheckeredPage, snapshot):
    # renders nothing if initial stack is not passed
    snapshot.assert_match(render(create_stack(initial_stack=[])), "nothing.png")

    # renders nothing if initial stack is empty
    snapshot.assert_match(render(create_stack(initial_stack=[])), "nothing.png")

    # renders page if initial_stack only has one item
    snapshot.assert_match(
        render(create_stack(initial_stack=[ImagePage])), "image-page.png"
    )

    # renders top page if initial_stack has more than one item
    snapshot.assert_match(
        render(
            create_stack(initial_stack=[ImagePage, ImagePage, ImagePage, CheckeredPage])
        ),
        "checkered-page.png",
    )


def test_transitions(create_stack, render, ImagePage, CheckeredPage, snapshot):
    component = create_stack(initial_stack=[ImagePage])

    # render so transitions are animated
    render(component)

    # can push
    component.push(CheckeredPage)
    sleep(0.3)
    snapshot.assert_match(render(component), "checkered-page.png")

    # can push after push
    component.push(ImagePage)
    sleep(0.3)
    snapshot.assert_match(render(component), "image-page.png")

    # can pop after push
    component.pop()
    sleep(0.3)
    snapshot.assert_match(render(component), "checkered-page.png")

    # can pop after pop
    component.pop()
    sleep(0.3)
    snapshot.assert_match(render(component), "image-page.png")

    # can pop last page off stack
    component.pop()
    sleep(0.3)
    snapshot.assert_match(render(component), "nothing.png")

    # pop does nothing when stack is empty
    component.pop()
    sleep(0.3)
    snapshot.assert_match(render(component), "nothing.png")


def test_transitions_without_animation(
    create_stack, render, ImagePage, CheckeredPage, snapshot
):
    component = create_stack(initial_stack=[ImagePage])

    # render so transitions are animated
    render(component)

    # can push
    component.push(CheckeredPage, animate=False)
    snapshot.assert_match(render(component), "checkered-page.png")

    # can push after push
    component.push(ImagePage, animate=False)
    snapshot.assert_match(render(component), "image-page.png")

    # can pop after push
    component.pop(animate=False)
    snapshot.assert_match(render(component), "checkered-page.png")

    # can pop after pop
    component.pop(animate=False)
    snapshot.assert_match(render(component), "image-page.png")

    # can pop last page off stack
    component.pop(animate=False)
    snapshot.assert_match(render(component), "nothing.png")

    # pop does nothing when stack is empty
    component.pop(animate=False)
    snapshot.assert_match(render(component), "nothing.png")


def test_transitions_before_render(
    create_stack, render, ImagePage, CheckeredPage, snapshot
):
    # pushing works and does not animate
    component = create_stack(initial_stack=[ImagePage])
    component.push(CheckeredPage)
    sleep(0.05)
    snapshot.assert_match(render(component), "checkered-page.png")

    # popping works and does not animate
    component = create_stack(initial_stack=[ImagePage, CheckeredPage])
    component.pop()
    sleep(0.05)
    snapshot.assert_match(render(component), "image-page.png")


def test_transitions_during_transition(
    create_stack, render, ImagePage, CheckeredPage, snapshot
):
    component = create_stack(initial_stack=[ImagePage])

    # check initial render correct
    snapshot.assert_match(render(component), "image-page.png")

    # pushing while pushing does nothing
    component.push(CheckeredPage)
    sleep(0.05)
    component.push(ImagePage)
    sleep(0.25)
    snapshot.assert_match(render(component), "checkered-page.png")

    # popping while pushing does nothing
    component.push(ImagePage)
    sleep(0.05)
    component.pop()
    sleep(0.25)
    snapshot.assert_match(render(component), "image-page.png")

    # popping while popping does nothing
    component.pop()
    sleep(0.05)
    component.pop()
    sleep(0.25)
    snapshot.assert_match(render(component), "checkered-page.png")

    # pushing while popping does nothing
    component.pop()
    sleep(0.05)
    component.push(CheckeredPage)
    sleep(0.25)
    snapshot.assert_match(render(component), "image-page.png")


def test_transition_animations(
    mocker, create_stack, render, ImagePage, CheckeredPage, snapshot
):
    def slow_transition(distance, duration):
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)

    mocker.patch(
        "pt_miniscreen.core.components.stack.transition", side_effect=slow_transition
    )

    component = create_stack()

    # render component so transitions are animated
    render(component)

    # pushing first component is animated correctly
    component.push(ImagePage)
    sleep(0.1)
    snapshot.assert_match(render(component), "push-first-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "push-first-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "push-first-3.png")

    # pushing a second component is animated correctly
    component.push(CheckeredPage)
    sleep(0.1)
    snapshot.assert_match(render(component), "push-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "push-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "push-3.png")

    # popping is animated correctly
    component.pop()
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-3.png")

    # popping last component is animated correctly
    component.pop()
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-last-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-last-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "pop-last-3.png")


def test_active_attributes(create_stack, ImagePage, CheckeredPage):
    # returns None when stack is empty
    component = create_stack()
    assert component.active_component is None
    assert component.active_index is None

    # returns the correct component and index when stack has one item
    component = create_stack(initial_stack=[ImagePage])
    assert isinstance(component.active_component, ImagePage)
    assert component.active_index == 0

    # returns the correct component and index when stack has more than item
    component = create_stack(
        initial_stack=[ImagePage, ImagePage, ImagePage, CheckeredPage]
    )
    assert isinstance(component.active_component, CheckeredPage)
    assert component.active_index == 3


def test_active_attributes_during_transitions(
    create_stack, render, ImagePage, CheckeredPage
):
    component = create_stack(initial_stack=[ImagePage, CheckeredPage])

    # render component so transition is animated
    render(component)

    # when popping
    component.pop()
    sleep(0.05)

    # returns the correct component and index
    assert isinstance(component.active_component, ImagePage)
    assert component.active_index == 0

    # returns the correct component and index when pop is finished
    sleep(0.25)
    assert isinstance(component.active_component, ImagePage)
    assert component.active_index == 0

    # when popping last item
    component.pop()
    sleep(0.05)

    # returns None
    assert component.active_component is None
    assert component.active_index is None

    # returns the correct component and index when pop is finished
    sleep(0.25)
    assert component.active_component is None
    assert component.active_index is None

    # when pushing
    component.push(CheckeredPage)
    sleep(0.05)

    # returns the correct component and index
    assert isinstance(component.active_component, CheckeredPage)
    assert component.active_index == 0

    # returns the correct component when push is finished
    sleep(0.25)
    assert isinstance(component.active_component, CheckeredPage)
    assert component.active_index == 0

    # when pushing onto another component
    component.push(ImagePage)
    sleep(0.05)

    # returns the correct component and index
    assert isinstance(component.active_component, ImagePage)
    assert component.active_index == 1

    # returns the correct component when push is finished
    sleep(0.25)
    assert isinstance(component.active_component, ImagePage)
    assert component.active_index == 1


def test_cleanup(parent, ImagePage, CheckeredPage):
    from pt_miniscreen.core.components import Stack

    component = ref(
        parent.create_child(Stack, initial_stack=[ImagePage, CheckeredPage])
    )

    # get reference to stack to check it is cleaned up
    stack = [ref(page) for page in component().state["stack"]]
    assert len(stack) > 0

    # remove list from parent and perform a garbage collection
    parent.remove_child(component())
    gc.collect()

    # component should be cleaned up
    assert component() is None

    # stack should be cleaned up
    for page in stack:
        assert page() is None


def test_cleanup_during_push(parent, render, ImagePage, CheckeredPage):
    from pt_miniscreen.core.components import Stack

    component = ref(
        parent.create_child(Stack, initial_stack=[ImagePage, CheckeredPage])
    )

    # render component so transitions animate
    render(component())

    # get reference to stack to check it is cleaned up
    stack = [ref(page) for page in component().state["stack"]]
    assert len(stack) > 0

    # start transition
    component().push(ImagePage)
    sleep(0.05)

    # remove list from parent
    parent.remove_child(component())

    # wait a tick to let transition bail and then perform a collection
    sleep(0.05)
    gc.collect()

    # component should be cleaned up
    assert component() is None

    # stack should be cleaned up
    for page in stack:
        assert page() is None


def test_cleanup_during_pop(parent, render, ImagePage, CheckeredPage):
    from pt_miniscreen.core.components import Stack

    component = ref(
        parent.create_child(Stack, initial_stack=[ImagePage, CheckeredPage])
    )

    # render component so transitions animate
    render(component())

    # get reference to stack to check it is cleaned up
    stack = [ref(page) for page in component().state["stack"]]
    assert len(stack) > 0

    # start transition
    component().pop()
    sleep(0.05)

    # remove list from parent
    parent.remove_child(component())

    # wait a tick to let transition bail and then perform a collection
    sleep(0.05)
    gc.collect()

    # component should be cleaned up
    assert component() is None

    # stack should be cleaned up
    for page in stack:
        assert page() is None
