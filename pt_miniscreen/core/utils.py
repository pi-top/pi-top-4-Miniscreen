from itertools import cycle
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


def checkered(image, box_size=4):
    draw = ImageDraw.Draw(image)
    y = 0
    x = 0
    offset_box = False

    while y < image.height:
        while x < image.width:
            # offset by a box size if offset_box is true
            x_pos = x + box_size if offset_box else x

            draw.rectangle(
                (x_pos, y, x_pos + box_size - 1, y + box_size - 1), fill="white"
            )

            # skip a box size so we checker the row
            x += box_size * 2

        # move down a row, back to left edge and change box offset for next row
        y += box_size
        x = 0
        offset_box = not offset_box

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
        if bold and not italics:
            return ImageFont.truetype("Roboto-Bold.ttf", size=size)

        if not bold and italics:
            return ImageFont.truetype("Roboto-Italic.ttf", size=size)

        if bold and italics:
            return ImageFont.truetype("Roboto-BoldItalic.ttf", size=size)

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

        # correct for lag time by increasing the size of the step
        corrected_step = base_step + floor(lag_time / step_duration)

        # clamp step so it does not cause us to travel more than distance
        clamped_step = min(corrected_step, distance - travelled)

        # calculate lag that has not been accounted for in the corrected step
        remaining_lag = lag_time % step_duration

        # correct for remaining lag in wait time
        sleep(max(step_duration - remaining_lag, 0))

        yield clamped_step

        travelled = travelled + clamped_step

    logger.debug(f"transition took {time() - start_time} seconds")


def carousel(end, start=0, step=1):
    forwards = list(range(start + step, end, step))
    backwards = list(range(end, start, -step))
    return cycle(forwards + backwards)
