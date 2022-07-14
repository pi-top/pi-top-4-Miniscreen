import gc
from functools import partial
from itertools import cycle, product, repeat
from os import path
from time import sleep
from weakref import ref

import pytest
from PIL import ImageFont

font_dir = f"{path.dirname(path.realpath(__file__))}/fonts"
vera_dir = f"{font_dir}/ttf-bitstream-vera"
roboto_dir = f"{font_dir}/roboto"


@pytest.fixture
def freeze_text(mocker):
    def carousel(end, start=0, step=1):
        return repeat(start)

    mocker.patch("pt_miniscreen.core.components.marquee_text.carousel", carousel)


@pytest.fixture
def create_marquee_text(create_component):
    from pt_miniscreen.core.components import MarqueeText

    return partial(create_component, MarqueeText)


@pytest.fixture
def TextStore():
    class TextStore:
        def __init__(self):
            self.update_count = 0

        def get_text(self):
            self.update_count += 1
            return f"get_text called \n{self.update_count} times"

    return TextStore


def test_text(freeze_text, create_marquee_text, render, snapshot):
    # can create component with no text
    snapshot.assert_match(render(create_marquee_text()), "no-text.png")

    # can create component with text
    snapshot.assert_match(render(create_marquee_text(text="Test text")), "text.png")

    # can create component with multi-line text
    component = create_marquee_text(text="Test multi-line\ntext")
    snapshot.assert_match(render(component), "multi-line-text.png")

    # can update text to be empty
    component.state.update({"text": ""})
    snapshot.assert_match(render(component), "no-text.png")

    # can update text to be multi-line again
    component.state.update({"text": "Test multi-line\ntext"})
    snapshot.assert_match(render(component), "multi-line-text.png")


def test_text_wrapping(freeze_text, create_marquee_text, render, snapshot):
    # component doesn't automatically wrap long text
    snapshot.assert_match(
        render(create_marquee_text(text="Automatically wrapped long text")),
        "no-wrap.png",
    )

    # component can't be set to wrap text
    snapshot.assert_match(
        render(create_marquee_text(text="Automatically wrapped long text", wrap=True)),
        "no-wrap.png",
    )

    # setting wrap in initial state also doesn't work
    snapshot.assert_match(
        render(
            create_marquee_text(
                text="Automatically wrapped long text", initial_state={"wrap": True}
            )
        ),
        "no-wrap.png",
    )


def test_text_styling(freeze_text, create_marquee_text, render, snapshot):
    text = "Test\ntext"

    # can remove spacing
    snapshot.assert_match(
        render(create_marquee_text(text=text, spacing=0)), "no-spacing.png"
    )

    # can set larger spacing
    snapshot.assert_match(
        render(create_marquee_text(text=text, spacing=10)), "large-spacing.png"
    )

    # can set font to be bold
    snapshot.assert_match(render(create_marquee_text(text=text, bold=True)), "bold.png")

    # can set font to be italic
    snapshot.assert_match(
        render(create_marquee_text(text=text, italics=True)), "italics.png"
    )

    # can set font to be big
    snapshot.assert_match(
        render(create_marquee_text(text=text, font_size=30)), "large-font.png"
    )

    # can set font to be small
    snapshot.assert_match(
        render(create_marquee_text(text=text, font_size=8)), "small-font.png"
    )

    # can set everything at once
    snapshot.assert_match(
        render(
            create_marquee_text(
                text=text, spacing=10, bold=True, italics=True, font_size=30
            )
        ),
        "everything.png",
    )


def test_text_fill(freeze_text, create_marquee_text, render, snapshot):
    # can set custom fill
    component = create_marquee_text(text="Test text", fill=0)
    snapshot.assert_match(render(component), "no-fill.png")

    # can update fill to show text again
    component.state.update({"fill": 1})
    snapshot.assert_match(render(component), "fill.png")

    # can update fill to hide text again
    component.state.update({"fill": 0})
    snapshot.assert_match(render(component), "no-fill.png")


def test_font(freeze_text, create_marquee_text, render, snapshot):
    # can set custom truetype font
    big_vera_mono_font = ImageFont.truetype(f"{vera_dir}/VeraMono.ttf", size=20)
    component = create_marquee_text(text="Test Text", font=big_vera_mono_font)
    snapshot.assert_match(render(component), "custom-font.png")

    # can update font
    component.state.update(
        {"font": ImageFont.truetype(f"{roboto_dir}/Roboto-Regular.ttf", size=10)}
    )
    snapshot.assert_match(render(component), "updated-font.png")


def test_get_text(freeze_text, create_marquee_text, TextStore, render, snapshot):
    # calls get_text on creation to populate text
    component = create_marquee_text(get_text=TextStore().get_text)
    snapshot.assert_match(render(component), "initial-text.png")

    # text not updated before one second has passed
    sleep(0.8)
    snapshot.assert_match(render(component), "initial-text.png")

    # text updated after one second from instantiation
    sleep(0.4)
    snapshot.assert_match(render(component), "updated-text-1.png")

    # text updated again after another second from instantiation
    sleep(1.3)
    snapshot.assert_match(render(component), "updated-text-2.png")


def test_get_text_interval(
    freeze_text, create_marquee_text, TextStore, render, snapshot
):
    component = create_marquee_text(
        get_text=TextStore().get_text, get_text_interval=0.5
    )

    # text not updated before half a second has passed
    sleep(0.4)
    snapshot.assert_match(render(component), "initial-text.png")

    # text updated after half a second has passed
    sleep(0.3)
    snapshot.assert_match(render(component), "updated-text-1.png")

    # text updated again after another half a second
    sleep(0.5)
    snapshot.assert_match(render(component), "updated-text-2.png")


def test_text_and_get_text_together(create_marquee_text, TextStore, render, snapshot):
    component = create_marquee_text(text="Initial text", get_text=TextStore().get_text)
    snapshot.assert_match(render(component), "initial_text.png")

    # text updated after one second
    sleep(1.2)
    snapshot.assert_match(render(component), "populated.png")


@pytest.mark.parametrize(
    "vertical_align,font_size",
    list(product(("top", "center", "bottom"), (8, 12, 16))),
)
def test_vertical_alignment(
    freeze_text, create_marquee_text, render, snapshot, vertical_align, font_size
):
    snapshot.assert_match(
        render(
            create_marquee_text(
                text="Multi-line\ntext",
                font_size=font_size,
                vertical_align=vertical_align,
            )
        ),
        "text-alignment.png",
    )


def test_align(freeze_text, create_marquee_text, render, snapshot):
    # align applies to text but not position
    snapshot.assert_match(
        render(create_marquee_text(text="Multi-line\ntext", align="center")),
        "center-align.png",
    )
    snapshot.assert_match(
        render(create_marquee_text(text="Multi-line\ntext", align="right")),
        "right-alignment.png",
    )


def test_updating_alignment(freeze_text, create_marquee_text, render, snapshot):
    component = create_marquee_text(text="Text\ntext")
    snapshot.assert_match(render(component), "initial_alignment.png")

    component.state.update({"vertical_align": "center"})
    snapshot.assert_match(render(component), "updated_alignment.png")


def test_scrolling(mocker, create_marquee_text, render, snapshot):
    def scroll(start, end):
        yield int((end - start) / 2)
        yield end
        yield int((end - start) / 2)
        yield start

    def carousel(end, start=0, step=1):
        return cycle(scroll(start, end))

    mocker.patch("pt_miniscreen.core.components.marquee_text.carousel", carousel)

    # doesn't scroll when text is thinner than image
    component = create_marquee_text(text="Small width")
    snapshot.assert_match(render(component), "small-width.png")
    sleep(0.15)
    snapshot.assert_match(render(component), "small-width.png")

    # scroll to end of text and back repeatedly when text is wider than image
    component = create_marquee_text(text="Medium width text")
    snapshot.assert_match(render(component), "medium-width-1.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "medium-width-2.png")
    sleep(0.115)
    snapshot.assert_match(render(component), "medium-width-3.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "medium-width-2.png")
    sleep(0.115)
    snapshot.assert_match(render(component), "medium-width-1.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "medium-width-2.png")

    sleep(0.115)

    # restarts scrolling when text changes and needs scrolling
    component.state.update({"text": "Very wide text that is super long"})
    snapshot.assert_match(render(component), "wide-text-1.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "wide-text-2.png")
    sleep(0.115)
    snapshot.assert_match(render(component), "wide-text-3.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "wide-text-2.png")
    sleep(0.115)
    snapshot.assert_match(render(component), "wide-text-1.png")
    # Wait for bounce time
    sleep(1.015)
    snapshot.assert_match(render(component), "wide-text-2.png")

    # stops scrolling when text changes to be thinner than image
    component.state.update({"text": "Small width"})
    sleep(0.15)
    snapshot.assert_match(render(component), "small-width.png")
    sleep(0.15)
    snapshot.assert_match(render(component), "small-width.png")


def test_set_active_pauses_scrolling(mocker, create_marquee_text, render, snapshot):
    def scroll(start, end):
        yield int((end - start) / 2)
        yield end
        yield int((end - start) / 2)
        yield start

    def carousel(end, start=0, step=1):
        return cycle(scroll(start, end))

    mocker.patch("pt_miniscreen.core.components.marquee_text.carousel", carousel)

    component = create_marquee_text(text="Very wide text that is super long")
    snapshot.assert_match(render(component), "wide-text-1.png")
    sleep(1.015)
    snapshot.assert_match(render(component), "wide-text-2.png")

    # stops scrolling when component is paused
    component._set_active(False)
    snapshot.assert_match(render(component), "wide-text-2.png")
    # Sleep for a time higher than bounce + step times
    sleep(1.2)
    snapshot.assert_match(render(component), "wide-text-2.png")

    # starts scrolling again when component is unpaused
    component._set_active(True)
    sleep(0.015)
    snapshot.assert_match(render(component), "wide-text-3.png")
    sleep(1.015)
    snapshot.assert_match(render(component), "wide-text-2.png")


def test_scrolling_step_time(create_marquee_text, render, snapshot):
    # can change step time
    component = create_marquee_text(text="Medium width text", step_time=0.3)
    snapshot.assert_match(render(component), "step-0.png")
    sleep(1.1)
    snapshot.assert_match(render(component), "step-1.png")
    sleep(0.4)
    snapshot.assert_match(render(component), "step-2.png")


def test_scrolling_step(create_marquee_text, render, snapshot):
    # can change step
    component = create_marquee_text(text="Medium width text", step=30)
    snapshot.assert_match(render(component), "step-0.png")
    sleep(1.015)
    snapshot.assert_match(render(component), "step-1.png")
    sleep(0.11)
    snapshot.assert_match(render(component), "step-2.png")


def test_cleanup(parent, render):
    from pt_miniscreen.core.components import MarqueeText

    component = ref(
        parent.create_child(MarqueeText, text="Very wide text that is super long")
    )

    # render component so scrolling starts
    render(component())

    # remove marquee text from parent
    parent.remove_child(component())

    # wait a step to let scrolling bail and then perform a collection
    sleep(1.2)
    gc.collect()

    # component should be cleaned up
    assert component() is None
