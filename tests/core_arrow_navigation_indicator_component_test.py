from functools import partial

import pytest


@pytest.fixture
def create_arrow_navigation_indicator(create_component):
    from pt_miniscreen.core.components import ArrowNavigationIndicator

    return partial(create_component, ArrowNavigationIndicator)


def test_set_arrow_visibility_on_constructor(
    create_arrow_navigation_indicator, render, snapshot
):
    snapshot.assert_match(
        render(create_arrow_navigation_indicator()), "both_visible.png"
    )

    component = create_arrow_navigation_indicator(upper_arrow_visible=False)
    snapshot.assert_match(render(component), "upper_arrow_not_visible.png")

    component = create_arrow_navigation_indicator(bottom_arrow_visible=False)
    snapshot.assert_match(render(component), "bottom_arrow_not_visible.png")

    component = create_arrow_navigation_indicator(
        upper_arrow_visible=False, bottom_arrow_visible=False
    )
    snapshot.assert_match(render(component), "both_not_visible.png")


def test_set_visibility_property(create_arrow_navigation_indicator, render, snapshot):
    component = create_arrow_navigation_indicator()

    component.upper_arrow_visible = False
    snapshot.assert_match(render(component), "upper_arrow_not_visible.png")
    component.upper_arrow_visible = True

    component.bottom_arrow_visible = False
    snapshot.assert_match(render(component), "bottom_arrow_not_visible.png")

    component.upper_arrow_visible = False
    snapshot.assert_match(render(component), "both_not_visible.png")
