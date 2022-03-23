from itertools import cycle, repeat
from logging import getLogger
from math import ceil, floor
from time import sleep, time

from PIL import Image, ImageDraw, ImageFont

logger = getLogger(__name__)

# rendering


def apply_layers(image, layers):
    for layer in layers:
        layer(image)

    return image


def layer(render, size, pos=(0, 0), transparent=True):
    bounding_box = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
    return lambda image: image.paste(
        render(image.crop(bounding_box) if transparent else Image.new("1", size)),
        pos,
    )


# render methods


def rectangle(image):
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, image.height), "white")
    return image


def corners(image):
    draw = ImageDraw.Draw(image)
    draw.point((0, 0), fill="white")
    draw.point((0, image.size[1] - 1), fill="white")
    draw.point((image.size[0] - 1, 0), fill="white")
    draw.point((image.size[0] - 1, image.size[1] - 1), fill="white")
    return image


# positioning


def offset_to_center(container, element, rounding_function=int):
    return rounding_function((container - element) / 2)


# text


def get_mono_font(size, bold=False, italics=False):
    if bold and not italics:
        return ImageFont.truetype("VeraMoBd.ttf", size=size)

    if not bold and italics:
        return ImageFont.truetype("VeraMoIt.ttf", size=size)

    if bold and italics:
        return ImageFont.truetype("VeraMoBI.ttf", size=size)

    return ImageFont.truetype("VeraMono.ttf", size=size)


def get_font(size, bold=False, italics=False):
    if size >= 12:
        return ImageFont.truetype("Roboto-Regular.ttf", size=size)

    return get_mono_font(size, bold, italics)


# image


def is_same_image(image_one, image_two) -> bool:
    try:
        return list(image_one.getdata()) == list(image_two.getdata())
    except Exception:
        return False


# generators


def transition(distance, duration, base_step=1):
    steps = ceil(distance / base_step)
    step_duration = duration / steps
    start_time = time()
    travelled = 0

    while travelled < distance:
        current_time = time()
        elapsed_time = current_time - start_time
        expected_time = duration * travelled / distance
        lag_time = max(elapsed_time - expected_time, 0)

        # reduce wait time by the lag that cannot be corrected in the step
        remaining_lag = lag_time % step_duration
        wait_time = max(step_duration - remaining_lag, 0)
        sleep(wait_time)

        # correct step for lag time by adding distance based on step_duration
        corrected_step = base_step + floor(lag_time / step_duration)

        # clamp step so it does not cause us to travel more than distance
        clamped_step = min(corrected_step, distance - travelled)

        yield clamped_step
        travelled = travelled + clamped_step

    logger.debug(f"transition took {time() - start_time} seconds")


def carousel(max_value, min_value=0, resolution=1):
    if max_value <= 0:
        return repeat(min_value)

    forwards = list(range(min_value, max_value, resolution))
    backwards = list(range(max_value, min_value, -resolution))
    return cycle(forwards + backwards)
