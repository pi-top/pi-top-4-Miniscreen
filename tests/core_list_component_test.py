from functools import partial
from math import ceil
from time import sleep

import pytest
from PIL import Image


@pytest.fixture
def create_list(create_component_factory):
    from pt_miniscreen.core.components import List

    return create_component_factory(List)


@pytest.fixture
def ImageRow(get_test_image_path):
    from pt_miniscreen.core.components import Image as ImageComponent

    return partial(
        ImageComponent,
        image_path=get_test_image_path("test-1.png"),
        resize=True,
        resize_resampling=Image.BOX,
    )


@pytest.fixture
def CheckeredRow():
    from pt_miniscreen.core import Component
    from pt_miniscreen.core.utils import checkered

    class Checkered(Component):
        def render(self, image):
            return checkered(image)

    return Checkered


@pytest.fixture
def create_rows(ImageRow, CheckeredRow):
    def create_rows(length, row_types=[ImageRow, CheckeredRow]):
        return [row_types[i % len(row_types)] for i in range(length)]

    return create_rows


def test_rows(create_list, create_rows, render, snapshot):
    try:
        create_list()
    except Exception as e:
        no_rows_exception = e
    finally:
        assert (
            str(no_rows_exception)
            == "__init__() missing 1 required positional argument: 'Rows'"
        )

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

    # can render an enormous amount more rows than visible
    snapshot.assert_match(
        render(create_list(Rows=create_rows(10000), num_visible_rows=5)),
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


def test_scrolling_before_render(create_list, create_rows, render, snapshot):
    # scrolling does not animate before initial render
    component = create_list(Rows=create_rows(5), num_visible_rows=3)
    component.scroll_down()
    sleep(0.05)
    snapshot.assert_match(render(component), "scroll_down_before_initial_render.png")

    # scrolling does not animate before initial render
    component = create_list(
        Rows=create_rows(5), num_visible_rows=3, initial_top_row_index=1
    )
    component.scroll_up()
    sleep(0.05)
    snapshot.assert_match(render(component), "scroll_up_before_initial_render.png")


def test_scrolling(create_list, create_rows, render, snapshot):
    pass


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
