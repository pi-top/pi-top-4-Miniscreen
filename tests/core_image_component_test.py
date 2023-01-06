import itertools
from functools import partial
from time import sleep

import pytest
from PIL import Image


@pytest.fixture
def create_image(create_component):
    from pt_miniscreen.core.components import Image as ImageComponent

    return partial(create_component, ImageComponent)


def test_image_path(create_image, render, get_test_image_path, snapshot):
    # can create image with no image_path
    snapshot.assert_match(render(create_image()), "no_image_path.png")

    # can create image with an image_path
    component = create_image(image_path=get_test_image_path("test-1.png"))
    snapshot.assert_match(render(component), "image_path.png")

    # can update image_path
    component.state.update({"image_path": get_test_image_path("test-2.png")})
    snapshot.assert_match(render(component), "updated_image_path.png")

    # can update image_path to None
    component.state.update({"image_path": None})
    snapshot.assert_match(render(component), "no_image_path.png")

    # changing image_path to animated image starts animating
    component.state.update({"image_path": get_test_image_path("test.gif")})
    snapshot.assert_match(render(component), "frame-1.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")

    # changing image_path resets the current frame
    component.state.update({"image_path": get_test_image_path("test-1.png")})
    component.state.update({"image_path": get_test_image_path("test.gif")})
    snapshot.assert_match(render(component), "frame-1.png")


def test_image_resize(create_image, render, get_test_image_path, snapshot):
    # can resize image to match input size
    component = create_image(image_path=get_test_image_path("test-1.png"), resize=True)
    snapshot.assert_match(render(component), "resize.png")

    # can change resize dynamically
    component.state.update({"resize": False})
    snapshot.assert_match(render(component), "resize_off.png")


def test_image_resize_resampling(create_image, render, get_test_image_path, snapshot):
    # can resize image with custom resampling
    component = create_image(
        image_path=get_test_image_path("test-1.png"),
        resize=True,
        resize_resampling=Image.BOX,
    )
    snapshot.assert_match(render(component), "box_resampling.png")

    # can change resampling dynamically
    component.state.update({"resize_resampling": Image.HAMMING})
    snapshot.assert_match(render(component), "hamming_resampling.png")


def test_animated_image(create_image, render, get_test_image_path, snapshot):
    component = create_image(image_path=get_test_image_path("test.gif"))

    # loops by default
    snapshot.assert_match(render(component), "frame-1.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")

    # doesn't move off current frame after changing loop to false
    component.state.update({"loop": False})
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")

    # can turn looping back on
    component.state.update({"loop": True})
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")

    # stops animating when component is paused
    component._set_active(False)
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")

    # starts animating again when component is unpaused
    component._set_active(True)
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-1.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")

    # can create image without looping
    component = create_image(image_path=get_test_image_path("test.gif"), loop=False)
    snapshot.assert_match(render(component), "frame-1.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")
    sleep(0.55)
    snapshot.assert_match(render(component), "frame-2.png")


def test_image_attribute(create_image, get_test_image_path):
    # image is None when there is no image_path
    component = create_image()
    assert component.image is None

    # can get image loaded using image_path from image attribute
    component = create_image(image_path=get_test_image_path("test-1.png"))
    assert isinstance(component.image, Image.Image)

    # mutating image does not change component image
    image = component.image
    image.putpixel((10, 10), 1)
    assert image != component.image

    # mutating resized image does not change component image
    component = create_image(image_path=get_test_image_path("test-1.png"), resize=True)
    image = component.image
    image.putpixel((10, 10), 1)
    assert image != component.image

    # cannot change image by setting image attribute
    try:
        component.image = None
    except Exception as e:
        set_image_attribute_error = e
    finally:
        assert (
            str(set_image_attribute_error)
            == "Setting image property directly not allowed, update image_path in state"
        )


@pytest.mark.parametrize(
    "align,vertical_align",
    list(itertools.product(("left", "center", "right"), ("top", "center", "bottom"))),
)
def test_alignment(
    create_image, render, get_test_image_path, snapshot, align, vertical_align
):
    snapshot.assert_match(
        render(
            create_image(
                image_path=get_test_image_path("test-1.png"),
                align=align,
                vertical_align=vertical_align,
            )
        ),
        "image-alignment.png",
    )


def test_updating_alignment(create_image, render, get_test_image_path, snapshot):
    component = create_image(image_path=get_test_image_path("test-1.png"))
    snapshot.assert_match(render(component), "initial_alignment.png")

    component.state.update({"align": "right", "vertical_align": "bottom"})
    snapshot.assert_match(render(component), "updated_alignment.png")
