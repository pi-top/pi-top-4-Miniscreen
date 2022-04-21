from functools import partial
from itertools import product
from os import path
from time import sleep

import pytest
from PIL import ImageFont

font_dir = f"{path.dirname(path.realpath(__file__))}/fonts"
vera_dir = f"{font_dir}/ttf-bitstream-vera"
roboto_dir = f"{font_dir}/roboto"


@pytest.fixture
def create_text(create_component):
    from pt_miniscreen.core.components import Text

    return partial(create_component, Text)


@pytest.fixture
def TextStore():
    class TextStore:
        def __init__(self):
            self.text = "Text updated 0 times"
            self.update_count = 0

        def get_text(self):
            text = self.text
            self.update_count += 1
            self.text = f"Text updated {self.update_count} times"
            return text

    return TextStore


def test_text(create_text, render, snapshot):
    # can create component with no text
    snapshot.assert_match(render(create_text()), "no-text.png")

    # can create component with text
    snapshot.assert_match(render(create_text(text="Test text")), "text.png")

    # can create component with multi-line text
    component = create_text(text="Test multi-line\ntext")
    snapshot.assert_match(render(component), "multi-line-text.png")

    # can update text to be empty
    component.state.update({"text": ""})
    snapshot.assert_match(render(component), "no-text.png")

    # can update text to be multi-line again
    component.state.update({"text": "Test multi-line\ntext"})
    snapshot.assert_match(render(component), "multi-line-text.png")


def test_text_wrapping(create_text, render, snapshot):
    # component automatically wraps long text
    component = create_text(text="Automatically wrapped long text")
    snapshot.assert_match(render(component), "wrap-on-text.png")

    # updated text still wraps
    component.state.update({"text": "Automatically wrapped long text updated"})
    snapshot.assert_match(render(component), "wrap-on-text-updated.png")

    # can turn off automatic wrapping
    component = create_text(text="Automatically wrapped long text", wrap=False)
    snapshot.assert_match(render(component), "wrap-off-text.png")

    # updated text doesn't wrap if wrapping is turned off
    component.state.update({"text": "Automatically wrapped long text updated"})
    snapshot.assert_match(render(component), "wrap-off-text-updated.png")


def test_text_styling(create_text, render, snapshot):
    text = "Test\ntext"

    # can remove spacing
    snapshot.assert_match(render(create_text(text=text, spacing=0)), "no-spacing.png")

    # can set larger spacing
    snapshot.assert_match(
        render(create_text(text=text, spacing=10)), "large-spacing.png"
    )

    # can set font to be bold
    snapshot.assert_match(render(create_text(text=text, bold=True)), "bold.png")

    # can set font to be italic
    snapshot.assert_match(render(create_text(text=text, italics=True)), "italics.png")

    # can set font to be big
    snapshot.assert_match(
        render(create_text(text=text, font_size=30)), "large-font.png"
    )

    # can set font to be small
    snapshot.assert_match(render(create_text(text=text, font_size=8)), "small-font.png")

    # can set everything at once
    snapshot.assert_match(
        render(
            create_text(text=text, spacing=10, bold=True, italics=True, font_size=30)
        ),
        "everything.png",
    )


def test_text_fill(create_text, render, snapshot):
    # can set custom fill
    component = create_text(text="Test text", fill=0)
    snapshot.assert_match(render(component), "no-fill.png")

    # can update fill to show text again
    component.state.update({"fill": 1})
    snapshot.assert_match(render(component), "fill.png")

    # can update fill to hide text again
    component.state.update({"fill": 0})
    snapshot.assert_match(render(component), "no-fill.png")


def test_font(create_text, render, snapshot):
    # can set custom truetype font
    big_vera_mono_font = ImageFont.truetype(f"{vera_dir}/VeraMono.ttf", size=20)
    component = create_text(text="Test Text", font=big_vera_mono_font)
    snapshot.assert_match(render(component), "custom-font.png")

    # can update font
    component.state.update(
        {"font": ImageFont.truetype(f"{roboto_dir}/Roboto-Regular.ttf", size=10)}
    )
    snapshot.assert_match(render(component), "updated-font.png")


def test_get_text(create_text, TextStore, render, snapshot):
    # calls get_text on creation to populate text
    component = create_text(get_text=TextStore().get_text)
    snapshot.assert_match(render(component), "initial-text.png")

    # text not updated before one second has passed
    sleep(0.9)
    snapshot.assert_match(render(component), "initial-text.png")

    # text updated after one second
    sleep(0.2)
    snapshot.assert_match(render(component), "updated-text-1.png")

    # text updated again after another second
    sleep(1)
    snapshot.assert_match(render(component), "updated-text-2.png")


def test_get_text_interval(create_text, TextStore, render, snapshot):
    component = create_text(get_text=TextStore().get_text, get_text_interval=0.5)

    # text not updated before half a second has passed
    sleep(0.4)
    snapshot.assert_match(render(component), "initial-text.png")

    # text updated after half a second has passed
    sleep(0.2)
    snapshot.assert_match(render(component), "updated-text-1.png")

    # text updated again after another half a second
    sleep(0.5)
    snapshot.assert_match(render(component), "updated-text-2.png")


def test_get_text_lazily(create_text, TextStore, render, snapshot):
    # doesn't call get_text to populate text when get_text_lazily passed
    component = create_text(get_text=TextStore().get_text, get_text_lazily=True)
    snapshot.assert_match(render(component), "not-populated.png")

    # text populated after one second
    sleep(1.1)
    snapshot.assert_match(render(component), "populated.png")


@pytest.mark.parametrize(
    "align,vertical_align,font_size",
    list(
        product(("left", "center", "right"), ("top", "center", "bottom"), (8, 12, 16))
    ),
)
def test_alignment(create_text, render, snapshot, align, vertical_align, font_size):
    snapshot.assert_match(
        render(
            create_text(
                text="Multi-line\ntext",
                font_size=font_size,
                align=align,
                vertical_align=vertical_align,
            )
        ),
        "text-alignment.png",
    )


def test_updating_alignment(create_text, render, snapshot):
    component = create_text(text="Text\ntext")
    snapshot.assert_match(render(component), "initial_alignment.png")

    component.state.update({"align": "right", "vertical_align": "bottom"})
    snapshot.assert_match(render(component), "updated_alignment.png")
