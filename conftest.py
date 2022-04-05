import io
from itertools import repeat
from os import path
from pathlib import Path
from sys import modules
from unittest.mock import MagicMock

import pytest
from PIL import Image, ImageFont

from pt_miniscreen.utils import get_image_file_path

pytest_plugins = ("pytest_snapshot", "tests.plugins.snapshot_reporter")


def patch_packages():
    modules_to_patch = [
        "pitop",
        "pitop.common.formatting",
        "pitop.common.command_runner",
        "pitop.common.pt_os",
    ]
    for module in modules_to_patch:
        modules[module] = MagicMock()

    # packages that need to be patched in tests
    from tests.mocks import battery, pitop, sys_info

    modules["pitop.common.sys_info"] = sys_info
    modules["pitop.battery"] = battery
    modules["pitop"] = pitop


def use_test_font(mocker):
    font_dir = f"{path.dirname(path.realpath(__file__))}/tests/fonts"
    vera_dir = f"{font_dir}/ttf-bitstream-vera"
    roboto_dir = f"{font_dir}/roboto"

    def get_mono_font(size, bold=False, italics=False):
        if bold and not italics:
            return ImageFont.truetype(f"{vera_dir}/VeraMoBd.ttf", size=size)

        if not bold and italics:
            return ImageFont.truetype(f"{vera_dir}/VeraMoIt.ttf", size=size)

        if bold and italics:
            return ImageFont.truetype(f"{vera_dir}/VeraMoBI.ttf", size=size)

        return ImageFont.truetype(f"{vera_dir}/VeraMono.ttf", size=size)

    def get_font(size, bold=False, italics=False):
        if size >= 12:
            return ImageFont.truetype(
                font=f"{roboto_dir}/Roboto-Regular.ttf", size=size
            )

        return get_mono_font(size, bold, italics)

    mocker.patch("pt_miniscreen.utils.get_font", get_font)
    mocker.patch("pt_miniscreen.utils.get_mono_font", get_mono_font)


def use_test_images(mocker):
    def get_path(relative_path):
        real_image = get_image_file_path(relative_path)
        test_image = real_image.replace("pt_miniscreen", "tests")
        return test_image if path.exists(test_image) else real_image

    mocker.patch("pt_miniscreen.utils.get_image_file_path", get_path)


def freeze_marquee_text(mocker):
    def carousel(max_value, min_value=0, resolution=1):
        return repeat(min_value)

    mocker.patch("pt_miniscreen.hotspots.templates.marquee_text.carousel", carousel)


def turn_off_bootsplash():
    bootsplash_breadcrumb = Path("/tmp/.com.pi-top.pt_miniscreen.boot-played")
    if not bootsplash_breadcrumb.is_file():
        bootsplash_breadcrumb.touch()


def mock_timeouts(timeout):
    from pt_miniscreen.state import State, timeouts

    timeouts[State.DIM] = timeout
    timeouts[State.SCREENSAVER] = timeout


def setup_test(mocker, screensaver_timeout=3600):
    mock_timeouts(timeout=screensaver_timeout)
    patch_packages()
    turn_off_bootsplash()
    use_test_font(mocker)
    use_test_images(mocker)
    freeze_marquee_text(mocker)


@pytest.fixture(autouse=True)
def app(mocker):
    setup_test(mocker)

    from pt_miniscreen.app import App

    app = App()
    app.start()

    yield app

    app.stop()


@pytest.fixture
def miniscreen(app):
    yield app.miniscreen


# Core test fixtures
@pytest.fixture
def render():
    def render(component, size=(128, 64)):
        image = component.render(Image.new("1", size))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    return render


@pytest.fixture
def create_component_factory():
    def create_component_factory(Component):
        class ParentlessComponent(Component):
            def __init__(self, **kwargs):
                super().__init__(**kwargs, on_rerender=self.dummy)

            def dummy(self):
                pass

        return ParentlessComponent

    return create_component_factory


@pytest.fixture
def get_test_image_path():
    def get_test_image_path(image_name):
        return path.abspath(
            path.join(Path(__file__).parent, "tests/images", image_name)
        )

    return get_test_image_path
