from functools import partial
from math import ceil
from time import sleep

import pytest
from PIL import Image


@pytest.fixture
def create_page_list(create_component):
    from pt_miniscreen.core.components import PageList

    return partial(create_component, PageList)


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


@pytest.fixture
def create_pages(ImagePage, CheckeredPage):
    def create_pages(length, page_types=[ImagePage, CheckeredPage]):
        return [page_types[i % len(page_types)] for i in range(length)]

    return create_pages


def test_pages(create_page_list, create_pages, render, snapshot):
    with pytest.raises(TypeError):
        create_page_list()

    # doesn't render anything if there are no rows
    snapshot.assert_match(render(create_page_list(Pages=[])), "no-pages.png")

    # fills the space if there is one row
    snapshot.assert_match(
        render(create_page_list(Pages=create_pages(1))), "one-page.png"
    )

    # splits the height equally if there are multiple rows
    snapshot.assert_match(
        render(create_page_list(Pages=create_pages(4))), "multiple-pages.png"
    )


def test_num_visible_rows(create_page_list, create_pages, render, snapshot):
    # setting num_visible_rows does nothing
    snapshot.assert_match(
        render(create_page_list(Pages=create_pages(3), num_visible_rows=2)),
        "num_visible_rows.png",
    )


def test_row_gap(create_page_list, create_pages, CheckeredPage, render, snapshot):
    create_checkered_pages = partial(create_pages, page_types=[CheckeredPage])

    # row gap does nothing
    snapshot.assert_match(
        render(create_page_list(Pages=create_checkered_pages(2), row_gap=20)),
        "row_gap.png",
    )


def test_scrolling_animation(mocker, create_page_list, create_pages, render, snapshot):
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

    component = create_page_list(Pages=create_pages(3))

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


def test_current_page_attribute(
    create_page_list, create_pages, render, ImagePage, CheckeredPage
):
    # returns the correct initial page
    component = create_page_list(Pages=create_pages(5))
    assert isinstance(component.current_page, ImagePage)

    # render component so transition is animated
    render(component)

    # when scrolling down
    component.scroll_down()
    sleep(0.05)

    # returns the page visible when scroll transition is finished
    assert isinstance(component.current_page, CheckeredPage)

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert isinstance(component.current_page, CheckeredPage)

    # when scrolling up
    component.scroll_up()
    sleep(0.05)

    # returns the same rows as when the up scroll transition is finished
    assert isinstance(component.current_page, ImagePage)

    # returns the correct rows when scroll is finished
    sleep(0.25)
    assert isinstance(component.current_page, ImagePage)
