import gc
from functools import partial
from math import ceil
from time import sleep
from weakref import ref

import pytest
from PIL import Image


@pytest.fixture
def create_list(create_component):
    from pt_miniscreen.core.components import List

    return partial(create_component, List)


@pytest.fixture
def ImageRow(get_test_image_path):
    from pt_miniscreen.core.components import Image as ImageComponent

    class ImageRow(ImageComponent):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs,
                image_path=get_test_image_path("test-1.png"),
                resize=True,
                resize_resampling=Image.Resampling.BOX,
            )

    return ImageRow


@pytest.fixture
def CheckeredRow():
    from pt_miniscreen.core import Component
    from pt_miniscreen.core.utils import checkered

    class Checkered(Component):
        def render(self, image):
            return checkered(image)

    return Checkered


@pytest.fixture
def NumberedRow():
    from pt_miniscreen.core.components import Text

    class NumberedRow(Text):
        def __init__(self, text, **kwargs):
            super().__init__(
                **kwargs,
                text=text,
                align="center",
                vertical_align="center",
            )

    return NumberedRow


@pytest.fixture
def create_rows(ImageRow, CheckeredRow):
    def create_rows(length, row_types=[ImageRow, CheckeredRow]):
        return [row_types[i % len(row_types)] for i in range(length)]

    return create_rows


@pytest.fixture
def create_numbered_rows(NumberedRow):
    def create_numbered_rows(length):
        return [partial(NumberedRow, text=f"{i+ 1}") for i in range(length)]

    return create_numbered_rows


def test_rows(create_list, create_rows, render, snapshot):
    with pytest.raises(TypeError):
        create_list()

    # doesn't render anything if there are no rows
    snapshot.assert_match(render(create_list(Rows=[])), "no-rows.png")

    # fills the space if there is one row
    snapshot.assert_match(render(create_list(Rows=create_rows(1))), "one-row.png")

    # splits the height equally if there are multiple rows
    snapshot.assert_match(render(create_list(Rows=create_rows(4))), "multiple-rows.png")


def test_num_visible_rows(create_list, create_rows, render, snapshot):
    # calculates row height based off num_visible_rows
    snapshot.assert_match(
        render(create_list(Rows=create_rows(1), num_visible_rows=2)),
        "less-rows-than-visible.png",
    )

    # doesn't render a scrollbar when number of rows matches num_visible_rows
    snapshot.assert_match(
        render(create_list(Rows=create_rows(2), num_visible_rows=2)),
        "same-rows-as-visible.png",
    )

    # renders a scrollbar when total number of rows exceeds num_visible_rows
    component = create_list(Rows=create_rows(4), num_visible_rows=3)
    snapshot.assert_match(render(component), "more-rows-than-visible.png")

    # can render many more rows than visible
    snapshot.assert_match(
        render(create_list(Rows=create_rows(20), num_visible_rows=4)),
        "many-more-rows-than-visible.png",
    )

    # can render an enormous amount more rows than visible when virtual
    snapshot.assert_match(
        render(create_list(Rows=create_rows(10000), virtual=True, num_visible_rows=5)),
        "enormous-amount-more-rows-than-visible.png",
    )


def test_row_gap(create_list, create_rows, CheckeredRow, render, snapshot):
    create_checkered_rows = partial(create_rows, row_types=[CheckeredRow])

    # row gap does nothing when there is one row and num_visible_rows is None
    snapshot.assert_match(
        render(create_list(Rows=create_checkered_rows(1), row_gap=3)),
        "one-row-without-num-visible-rows.png",
    )

    # row gap works when there are multiple rows and num_visible_rows is None
    snapshot.assert_match(
        render(create_list(Rows=create_checkered_rows(2), row_gap=3)),
        "multiple-rows-without-num-visible-rows.png",
    )

    # row gap works when there are less rows than visible
    snapshot.assert_match(
        render(
            create_list(Rows=create_checkered_rows(2), num_visible_rows=4, row_gap=4)
        ),
        "less-rows-than-num-visible-rows.png",
    )

    # row gap works when there are the same rows as visible
    snapshot.assert_match(
        render(
            create_list(Rows=create_checkered_rows(4), num_visible_rows=4, row_gap=5)
        ),
        "same-rows-as-num-visible-rows.png",
    )

    # row gap works when there are more rows than visible
    component = create_list(
        Rows=create_checkered_rows(10), num_visible_rows=4, row_gap=6
    )
    snapshot.assert_match(
        render(component),
        "more-rows-than-num-visible-rows.png",
    )

    # can update row_gap
    component.state.update({"row_gap": 10})
    snapshot.assert_match(
        render(component),
        "more-rows-than-num-visible-rows-updated-gap.png",
    )


def test_unscrollable_lists(create_list, create_rows, render, snapshot):
    # scrolling does nothing when there are no rows
    component = create_list(Rows=[])
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "no-rows.png")
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "no-rows.png")

    # scrolling does nothing when there num_visible_rows is None
    component = create_list(Rows=create_rows(5))
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "rows-without-num-visible-rows.png")
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "rows-without-num-visible-rows.png")

    # scrolling does nothing when num rows is less than num_visible_rows
    component = create_list(Rows=create_rows(2), num_visible_rows=3)
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "less-rows-than-num-visible-rows.png")
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "less-rows-than-num-visible-rows.png")

    # scrolling does nothing when num rows matches num_visible_rows
    component = create_list(Rows=create_rows(3), num_visible_rows=3)
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "same-rows-as-num-visible-rows.png")
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "same-rows-as-num-visible-rows.png")


def test_scrolling(create_list, create_rows, render, snapshot):
    component = create_list(Rows=create_rows(5), num_visible_rows=2)

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_scrolling_down_moves_to(position):
        component.scroll_down()
        sleep(0.3)
        assert_in_position(position)

    def assert_scrolling_up_moves_to(position):
        component.scroll_up()
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling up when at top does nothing
    assert_scrolling_up_moves_to(1)

    # can scroll down
    assert_scrolling_down_moves_to(2)
    assert_scrolling_down_moves_to(3)

    # can scroll up when in middle of list
    assert_scrolling_up_moves_to(2)

    # can continue scrolling down after scrolling up
    assert_scrolling_down_moves_to(3)
    assert_scrolling_down_moves_to(4)

    # scrolling down when at bottom does nothing
    assert_scrolling_down_moves_to(4)

    # can scroll up to top
    assert_scrolling_up_moves_to(3)
    assert_scrolling_up_moves_to(2)
    assert_scrolling_up_moves_to(1)

    # scrolling up still does nothing
    assert_scrolling_up_moves_to(1)


def test_virtual_list_scrolling(create_list, create_rows, render, snapshot):
    component = create_list(Rows=create_rows(5), num_visible_rows=2, virtual=True)

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_scrolling_down_moves_to(position):
        component.scroll_down()
        sleep(0.3)
        assert_in_position(position)

    def assert_scrolling_up_moves_to(position):
        component.scroll_up()
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling up when at top does nothing
    assert_scrolling_up_moves_to(1)

    # can scroll down
    assert_scrolling_down_moves_to(2)
    assert_scrolling_down_moves_to(3)

    # can scroll up when in middle of list
    assert_scrolling_up_moves_to(2)

    # can continue scrolling down after scrolling up
    assert_scrolling_down_moves_to(3)
    assert_scrolling_down_moves_to(4)

    # scrolling down when at bottom does nothing
    assert_scrolling_down_moves_to(4)

    # can scroll up to top
    assert_scrolling_up_moves_to(3)
    assert_scrolling_up_moves_to(2)
    assert_scrolling_up_moves_to(1)

    # scrolling up still does nothing
    assert_scrolling_up_moves_to(1)


def test_scrolling_before_render(create_list, create_rows, render, snapshot):
    # scrolling does not animate before initial render
    component = create_list(Rows=create_rows(5), num_visible_rows=3)
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "scroll-down-before-initial-render.png")

    # scrolling does not animate before initial render
    component = create_list(
        Rows=create_rows(5), num_visible_rows=3, initial_top_row_index=1
    )
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "scroll-up-before-initial-render.png")


def test_scrolling_during_transition(create_list, create_rows, render, snapshot):
    component = create_list(Rows=create_rows(5), num_visible_rows=3)

    # check initial render correct
    snapshot.assert_match(render(component), "position-1.png")

    # scrolling down while transitioning down does nothing
    component.scroll_down()
    sleep(0.05)
    component.scroll_down()
    sleep(0.25)
    snapshot.assert_match(render(component), "position-2.png")

    # scrolling up while transitioning down nothing
    component.scroll_down()
    sleep(0.05)
    component.scroll_up()
    sleep(0.25)
    snapshot.assert_match(render(component), "position-3.png")

    # scrolling up while transitioning up nothing
    component.scroll_up()
    sleep(0.05)
    component.scroll_up()
    sleep(0.25)
    snapshot.assert_match(render(component), "position-2.png")

    # scrolling down while transitioning up nothing
    component.scroll_up()
    sleep(0.05)
    component.scroll_down()
    sleep(0.25)
    snapshot.assert_match(render(component), "position-1.png")


def test_scrolling_animation(mocker, create_list, create_rows, render, snapshot):
    def slow_transition(distance, duration):
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)

    mocker.patch(
        "pt_miniscreen.core.components.list.transition", side_effect=slow_transition
    )

    component = create_list(Rows=create_rows(3), num_visible_rows=2)

    # render component so scrolling is animated
    render(component)

    # scrolling down is animated correctly
    component.scroll_down()
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-3.png")

    # scrolling up is animated correctly
    component.scroll_up()
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-3.png")


def test_virtual_list_scrolling_animation(
    mocker, create_list, create_rows, render, snapshot
):
    def slow_transition(distance, duration):
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)
        sleep(duration / 3)
        yield ceil(distance / 3)

    mocker.patch(
        "pt_miniscreen.core.components.list.transition", side_effect=slow_transition
    )

    component = create_list(Rows=create_rows(3), num_visible_rows=2, virtual=True)

    # render component so scrolling is animated
    render(component)

    # scrolling down is animated correctly
    component.scroll_down()
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-down-3.png")

    # scrolling up is animated correctly
    component.scroll_up()
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-1.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-2.png")
    sleep(0.1)
    snapshot.assert_match(render(component), "scroll-up-3.png")


def test_scroll_with_distance_parameter(
    create_list, create_numbered_rows, render, snapshot
):
    component = create_list(Rows=create_numbered_rows(5), num_visible_rows=2)

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_scrolling_down_moves_to(distance, position):
        component.scroll_down(distance=distance)
        sleep(0.3)
        assert_in_position(position)

    def assert_scrolling_up_moves_to(distance, position):
        component.scroll_up(distance=distance)
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling up when at top does nothing
    assert_scrolling_up_moves_to(distance=3, position=1)

    # can scroll down using the distance parameter
    assert_scrolling_down_moves_to(distance=1, position=2)
    assert_scrolling_down_moves_to(distance=2, position=4)

    # can scroll up when in middle of list using the distance parameter
    assert_scrolling_up_moves_to(distance=1, position=3)
    assert_scrolling_up_moves_to(distance=2, position=1)

    # can continue scrolling down after scrolling up
    assert_scrolling_down_moves_to(distance=3, position=4)

    # scrolling down when at bottom does nothing
    assert_scrolling_down_moves_to(distance=2, position=4)


def test_virtual_list_scroll_with_distance_parameter(
    create_list, create_numbered_rows, render, snapshot
):
    component = create_list(
        Rows=create_numbered_rows(5), num_visible_rows=2, virtual=True
    )

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_scrolling_down_moves_to(distance, position):
        component.scroll_down(distance=distance)
        sleep(0.3)
        assert_in_position(position)

    def assert_scrolling_up_moves_to(distance, position):
        component.scroll_up(distance=distance)
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling up when at top does nothing
    assert_scrolling_up_moves_to(distance=3, position=1)

    # can scroll down using the distance parameter
    assert_scrolling_down_moves_to(distance=1, position=2)
    assert_scrolling_down_moves_to(distance=2, position=4)

    # can scroll up when in middle of list using the distance parameter
    assert_scrolling_up_moves_to(distance=1, position=3)
    assert_scrolling_up_moves_to(distance=2, position=1)

    # can continue scrolling down after scrolling up
    assert_scrolling_down_moves_to(distance=3, position=4)

    # scrolling down when at bottom does nothing
    assert_scrolling_down_moves_to(distance=2, position=4)


def test_scroll_to_top_and_bottom_methods(
    create_list, create_numbered_rows, render, snapshot
):
    component = create_list(Rows=create_numbered_rows(5), num_visible_rows=2)

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_to_bottom_moves_to(position):
        component.scroll_to_bottom()
        sleep(0.3)
        assert_in_position(position)

    def assert_to_top_moves_to(position):
        component.scroll_to_top()
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling to bottom moves to last position
    assert_to_bottom_moves_to(position=4)

    # scrolling to bottom again does nothing
    assert_to_bottom_moves_to(position=4)

    # scrolling to top moves to initial position
    assert_to_top_moves_to(position=1)

    # scrolling to top again does nothing
    assert_to_top_moves_to(position=1)


def test_virtual_list_scroll_to_top_and_bottom_methods(
    create_list, create_numbered_rows, render, snapshot
):
    component = create_list(
        Rows=create_numbered_rows(5), num_visible_rows=2, virtual=True
    )

    # render component so transitions are run
    render(component)

    def assert_in_position(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_to_bottom_moves_to(position):
        component.scroll_to_bottom()
        sleep(0.3)
        assert_in_position(position)

    def assert_to_top_moves_to(position):
        component.scroll_to_top()
        sleep(0.3)
        assert_in_position(position)

    # check initial render is correct
    assert_in_position(1)

    # scrolling to bottom moves to last position
    assert_to_bottom_moves_to(position=4)

    # scrolling to bottom again does nothing
    assert_to_bottom_moves_to(position=4)

    # scrolling to top moves to initial position
    assert_to_top_moves_to(position=1)

    # scrolling to top again does nothing
    assert_to_top_moves_to(position=1)


def test_visible_rows_attribute(
    create_list, create_rows, render, ImageRow, CheckeredRow
):
    # returns the same number of rows as num_visible_rows
    for num in range(1, 5):
        assert (
            len(create_list(Rows=create_rows(5), num_visible_rows=num).visible_rows)
            == num
        )

    # returns the correct initial rows
    component = create_list(Rows=create_rows(5), num_visible_rows=2)
    assert len(component.visible_rows) == 2
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # render component so transition is animated
    render(component)

    # when scrolling down
    component.scroll_down()
    sleep(0.05)

    # returns the same number of rows as visible
    assert len(component.visible_rows) == 2

    # returns the same rows as when the down scroll transition is finished
    assert component.visible_rows[0] is component.rows[1]
    assert component.visible_rows[1] is component.rows[2]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert component.visible_rows[0] is component.rows[1]
    assert component.visible_rows[1] is component.rows[2]

    # when scrolling up
    component.scroll_up()
    sleep(0.05)

    # returns the same number of rows as visible
    assert len(component.visible_rows) == 2

    # returns the same rows as when the up scroll transition is finished
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # when scrolling down with a distance greater than one
    component.scroll_down(distance=2)
    sleep(0.05)

    # returns the same number of rows as num_visible_rows
    assert len(component.visible_rows) == 2

    # returns the last two rows
    assert component.visible_rows[0] is component.rows[2]
    assert component.visible_rows[1] is component.rows[3]

    # returns the correct rows after scrolling is finished
    sleep(0.25)
    assert len(component.visible_rows) == 2
    assert component.visible_rows[0] is component.rows[2]
    assert component.visible_rows[1] is component.rows[3]

    # when scrolling up a distance greater than one
    component.scroll_up(distance=2)
    sleep(0.05)

    # returns the same number of rows as num_visible_rows
    assert len(component.visible_rows) == 2

    # returns the first two rows
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert len(component.visible_rows) == 2
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]


def test_virtual_list_visible_rows_attribute(
    create_list, create_rows, render, ImageRow, CheckeredRow
):
    # returns the same number of rows as num_visible_rows
    for num in range(1, 5):
        assert (
            len(
                create_list(
                    Rows=create_rows(5), num_visible_rows=num, virtual=True
                ).visible_rows
            )
            == num
        )

    # returns the correct initial rows
    component = create_list(Rows=create_rows(5), num_visible_rows=2, virtual=True)
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # render component so transition is animated
    render(component)

    # when scrolling down
    component.scroll_down()
    sleep(0.05)

    # returns the same number of rows as visible
    assert len(component.rows) == 3
    assert len(component.visible_rows) == 2

    # returns the same rows as when the down scroll transition is finished
    assert component.visible_rows[0] is component.rows[1]
    assert component.visible_rows[1] is component.rows[2]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert len(component.rows) == 2
    assert component.rows == component.visible_rows

    # when scrolling up
    component.scroll_up()
    sleep(0.05)

    # returns the same number of rows as visible
    assert len(component.visible_rows) == 2

    # returns the same rows as when the up scroll transition is finished
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert len(component.rows) == 2
    assert component.rows == component.visible_rows

    # when scrolling down with a distance greater than one
    component.scroll_down(distance=2)
    sleep(0.05)

    # returns the same number of rows as num_visible_rows
    assert len(component.rows) == 4
    assert len(component.visible_rows) == 2

    # returns the last two rows
    assert component.visible_rows[0] is component.rows[2]
    assert component.visible_rows[1] is component.rows[3]

    # returns the correct rows after scrolling is finished
    sleep(0.25)
    assert len(component.rows) == 2
    assert component.rows == component.visible_rows

    # when scrolling up a distance greater than one
    component.scroll_up(distance=2)
    sleep(0.05)

    # returns the same number of rows as num_visible_rows
    assert len(component.rows) == 4
    assert len(component.visible_rows) == 2

    # returns the first two rows
    assert component.visible_rows[0] is component.rows[0]
    assert component.visible_rows[1] is component.rows[1]

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert len(component.rows) == 2
    assert component.rows == component.visible_rows


def test_row_pausing(create_list, create_rows, render):
    component = create_list(Rows=create_rows(4), num_visible_rows=2)

    # rows are not active before list is rendered
    for row in component.rows:
        assert row.active_event.is_set() is False

    # only visible rows become active when rendered
    render(component)

    assert component.rows[0].active_event.is_set()
    assert component.rows[1].active_event.is_set()
    assert component.rows[2].active_event.is_set() is False
    assert component.rows[3].active_event.is_set() is False

    # correct rows are active after scrolling down
    component.scroll_down()
    sleep(0.30)
    assert component.rows[0].active_event.is_set() is False
    assert component.rows[1].active_event.is_set()
    assert component.rows[2].active_event.is_set()
    assert component.rows[3].active_event.is_set() is False

    # correct rows are active after scrolling up
    component.scroll_up()
    sleep(0.30)
    assert component.rows[0].active_event.is_set()
    assert component.rows[1].active_event.is_set()
    assert component.rows[2].active_event.is_set() is False
    assert component.rows[3].active_event.is_set() is False

    # correct rows are active after scrolling down with a distance more than one
    component.scroll_down(distance=2)
    sleep(0.30)
    assert component.rows[0].active_event.is_set() is False
    assert component.rows[1].active_event.is_set() is False
    assert component.rows[2].active_event.is_set()
    assert component.rows[3].active_event.is_set()

    # correct rows are active after scrolling up with a distance more than one
    component.scroll_up(distance=2)
    sleep(0.30)
    assert component.rows[0].active_event.is_set()
    assert component.rows[1].active_event.is_set()
    assert component.rows[2].active_event.is_set() is False
    assert component.rows[3].active_event.is_set() is False


def test_cleanup(parent, create_rows, render):
    from pt_miniscreen.core.components import List

    component = ref(parent.create_child(List, Rows=create_rows(5), num_visible_rows=3))

    # render component so transitions animate
    render(component())

    # get reference to middle row to check it is cleaned up
    row = ref(component().rows[1])

    # start transition
    component().scroll_down()
    sleep(0.05)

    # remove list from parent
    parent.remove_child(component())

    # wait a step to let transition bail and then perform a collection
    sleep(0.05)
    gc.collect()

    # component should be cleaned up
    assert component() is None

    # rows should be cleaned up
    assert row() is None


def test_row_cleanup_after_scrolling(create_list, create_rows, get_test_image_path):
    # lists keep rows alive when scrolled out of view
    component = create_list(Rows=create_rows(2), num_visible_rows=1)
    row = component.visible_rows[0]
    row.state.update({"image_path": get_test_image_path("test-2.png")})
    component.scroll_down()
    sleep(0.30)
    component.scroll_up()
    sleep(0.30)
    assert row is component.visible_rows[0]
    assert component.visible_rows[0].state["image_path"] == get_test_image_path(
        "test-2.png"
    )

    # virtual lists cleanup rows that are scrolled out of view
    component = create_list(Rows=create_rows(2), num_visible_rows=1, virtual=True)
    row = ref(component.visible_rows[0])
    row().state.update({"image_path": get_test_image_path("test-2.png")})
    component.scroll_down()
    sleep(0.30)
    component.scroll_up()
    sleep(0.30)
    assert row() is not component.visible_rows[0]
    assert component.visible_rows[0].state["image_path"] == get_test_image_path(
        "test-1.png"
    )

    # rows that are scrolled out of view are cleaned up at the next garbage collection
    gc.collect()
    assert row() is None
