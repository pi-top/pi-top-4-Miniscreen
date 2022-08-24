import gc
from functools import partial
from time import sleep
from weakref import ref

import pytest
from PIL import Image


@pytest.fixture
def create_selectable_list(create_component):
    from pt_miniscreen.core.components import SelectableList

    return partial(create_component, SelectableList)


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


# def test_rows(create_selectable_list, create_rows, render, snapshot):
#     try:
#         create_selectable_list()
#     except Exception as e:
#         no_rows_exception = e
#     finally:
#         assert (
#             str(no_rows_exception)
#             == "__init__() missing 1 required positional argument: 'Rows'"
#         )
#
#     # doesn't render anything if there are no rows
#     snapshot.assert_match(render(create_selectable_list(Rows=[])), "no-rows.png")
#
#     # fills the space if there is one row
#     snapshot.assert_match(render(create_selectable_list(Rows=create_rows(1))), "one-row.png")
#
#     # splits the height equally if there are multiple rows
#     snapshot.assert_match(render(create_selectable_list(Rows=create_rows(4))), "multiple-rows.png")


def test_num_visible_rows(create_selectable_list, create_rows, render, snapshot):
    # calculates row height based off num_visible_rows
    snapshot.assert_match(
        render(create_selectable_list(Rows=create_rows(1), num_visible_rows=2)),
        "less-rows-than-visible.png",
    )

    # doesn't render a scrollbar when number of rows matches num_visible_rows
    snapshot.assert_match(
        render(create_selectable_list(Rows=create_rows(2), num_visible_rows=2)),
        "same-rows-as-visible.png",
    )

    # renders a scrollbar when total number of rows exceeds num_visible_rows
    component = create_selectable_list(Rows=create_rows(4), num_visible_rows=3)
    snapshot.assert_match(render(component), "more-rows-than-visible.png")

    # can render many more rows than visible
    snapshot.assert_match(
        render(create_selectable_list(Rows=create_rows(20), num_visible_rows=4)),
        "many-more-rows-than-visible.png",
    )

    # can render an enormous amount more rows than visible when virtual
    snapshot.assert_match(
        render(
            create_selectable_list(
                Rows=create_rows(10000), virtual=True, num_visible_rows=5
            )
        ),
        "enormous-amount-more-rows-than-visible.png",
    )


def test_row_gap(create_selectable_list, create_rows, CheckeredRow, render, snapshot):
    create_checkered_rows = partial(create_rows, row_types=[CheckeredRow])

    # row gap does nothing when there is one row and num_visible_rows is None
    snapshot.assert_match(
        render(create_selectable_list(Rows=create_checkered_rows(1), row_gap=3)),
        "one-row-without-num-visible-rows.png",
    )

    # row gap works when there are multiple rows and num_visible_rows is None
    snapshot.assert_match(
        render(create_selectable_list(Rows=create_checkered_rows(2), row_gap=3)),
        "multiple-rows-without-num-visible-rows.png",
    )

    # row gap works when there are less rows than visible
    snapshot.assert_match(
        render(
            create_selectable_list(
                Rows=create_checkered_rows(2), num_visible_rows=4, row_gap=4
            )
        ),
        "less-rows-than-num-visible-rows.png",
    )

    # row gap works when there are the same rows as visible
    snapshot.assert_match(
        render(
            create_selectable_list(
                Rows=create_checkered_rows(4), num_visible_rows=4, row_gap=5
            )
        ),
        "same-rows-as-num-visible-rows.png",
    )

    # row gap works when there are more rows than visible
    component = create_selectable_list(
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


def test_lists_that_cant_select_next_or_previous(
    create_selectable_list, create_rows, render, snapshot
):
    # selecting next/previous does nothing when there are no rows
    component = create_selectable_list(Rows=[])
    component.select_next_row()
    sleep(0.05)
    snapshot.assert_match(render(component), "no-rows.png")
    component.select_previous_row()
    sleep(0.05)
    snapshot.assert_match(render(component), "no-rows.png")

    # selecting next/previous does nothing when num rows is less than num_visible_rows
    component = create_selectable_list(Rows=create_rows(1), num_visible_rows=2)
    component.select_next_row()
    sleep(0.05)
    snapshot.assert_match(render(component), "less-rows-than-num-visible-rows.png")
    component.select_previous_row()
    sleep(0.05)
    snapshot.assert_match(render(component), "less-rows-than-num-visible-rows.png")


def test_select_next_and_previous(
    create_selectable_list, create_rows, render, snapshot
):
    component = create_selectable_list(Rows=create_rows(4), num_visible_rows=3)

    # render component so transitions are run
    render(component)

    def assert_selected_row_is(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_select_next_row_selects_row(position):
        component.select_next_row()
        sleep(0.3)
        assert_selected_row_is(position)

    def assert_select_previous_row_selects_row(position):
        component.select_previous_row()
        sleep(0.3)
        assert_selected_row_is(position)

    # check initial render is correct
    assert_selected_row_is(1)

    # selecting previous row when at top does nothing
    assert_select_previous_row_selects_row(1)

    # can select next
    assert_select_next_row_selects_row(2)
    assert_select_next_row_selects_row(3)

    # can select previous when in middle of list
    assert_select_previous_row_selects_row(2)

    # can continue selecting next after selecting previous row
    assert_select_next_row_selects_row(3)
    assert_select_next_row_selects_row(4)

    # select next when at bottom does nothing
    assert_select_next_row_selects_row(4)

    # can navigate back to top
    component.select_previous_row()
    component.select_previous_row()
    component.select_previous_row()
    assert_select_previous_row_selects_row(1)

    # selecting previous row still does nothing
    assert_select_previous_row_selects_row(1)


def test_virtual_selectable_lists_select_next_and_previous(
    create_selectable_list, create_rows, render, snapshot
):
    component = create_selectable_list(
        Rows=create_rows(4), num_visible_rows=3, virtual=True
    )

    # render component so transitions are run
    render(component)

    def assert_selected_row_is(position):
        snapshot.assert_match(render(component), f"position-{position}.png")

    def assert_select_next_row_selects_row(position):
        component.select_next_row()
        sleep(0.3)
        assert_selected_row_is(position)

    def assert_select_previous_row_selects_row(position):
        component.select_previous_row()
        sleep(0.3)
        assert_selected_row_is(position)

    # check initial render is correct
    assert_selected_row_is(1)

    # selecting previous row when at top does nothing
    assert_select_previous_row_selects_row(1)

    # can select next
    assert_select_next_row_selects_row(2)
    assert_select_next_row_selects_row(3)

    # can select previous when in middle of list
    assert_select_previous_row_selects_row(2)

    # can continue selecting next after selecting previous row
    assert_select_next_row_selects_row(3)
    assert_select_next_row_selects_row(4)

    # select next when at bottom does nothing
    assert_select_next_row_selects_row(4)

    # can navigate back to top
    component.select_previous_row()
    component.select_previous_row()
    component.select_previous_row()
    assert_select_previous_row_selects_row(1)

    # selecting previous row still does nothing
    assert_select_previous_row_selects_row(1)


def test_select_before_render(create_selectable_list, create_rows, render, snapshot):
    # selecting next does not animate before initial render
    component = create_selectable_list(Rows=create_rows(5), num_visible_rows=3)
    component.select_next_row()
    sleep(0.05)
    snapshot.assert_match(
        render(component), "select-next-row-before-initial-render.png"
    )

    # selecting next does not animate before initial render
    component = create_selectable_list(
        Rows=create_rows(5), num_visible_rows=3, initial_top_row_index=1
    )
    component.select_previous_row()
    sleep(0.05)
    snapshot.assert_match(
        render(component), "select-previous-row-before-initial-render.png"
    )


def test_cleanup(parent, create_rows, render):
    from pt_miniscreen.core.components import SelectableList

    component = ref(
        parent.create_child(SelectableList, Rows=create_rows(5), num_visible_rows=3)
    )

    # render component so transitions animate
    render(component())

    # get reference to middle row to check it is cleaned up
    row = ref(component().rows[1])

    component().select_next_row()
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
