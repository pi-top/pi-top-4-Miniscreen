import logging
from random import randrange

import PIL.Image
import PIL.ImageDraw

from pt_miniscreen.core import Component
from pt_miniscreen.core.utils import apply_layers, layer

logger = logging.getLogger(__name__)


# Adapted from https://github.com/rm-hull/luma.examples/blob/master/examples/starfield.py


class StarfieldScreensaver(Component):
    SCREENSAVER_MAX_NO_OF_STARS = 150

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.star_array = self.create_child(
            StarArray, star_number=self.SCREENSAVER_MAX_NO_OF_STARS
        )
        self.create_interval(self.star_array.update, timeout=0.05)

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.star_array.render, size=(image.width, image.height), pos=(0, 0)
                )
            ],
        )


class Star:
    MAX_DEPTH = 32
    DELTA_Z = 0.19

    def __init__(self):
        self.x = randrange(-25, 25)
        self.y = randrange(-25, 25)
        self.z = randrange(1, self.MAX_DEPTH)

    def update(self):
        new_z = self.z - self.DELTA_Z

        # Star has moved 'past the display'
        if new_z <= 0:
            # Reposition far away from the screen (Z=max_depth)
            # with random X and Y coordinates
            self.x = randrange(-25, 25)
            self.y = randrange(-25, 25)
            self.z = self.MAX_DEPTH
        else:
            self.z = new_z


class StarArray(Component):
    SCREENSAVER_MAX_DEPTH = 32

    def __init__(self, star_number, **kwargs):
        super().__init__(**kwargs, initial_state={})

        self.stars = [Star() for _ in range(star_number)]

    def update(self):
        for star in self.stars:
            star.update()
        self.state.update({"x": randrange(1, 10000)})

    def render(self, image):
        origin_x = image.width // 2
        origin_y = image.height // 2

        draw = PIL.ImageDraw.Draw(image)

        for star in self.stars:
            # Convert 3D coordinates to 2D using perspective projection
            k = image.height / star.z
            x = int(star.x * k + origin_x)
            y = int(star.y * k + origin_y)

            # Draw star if visible
            if 0 <= x < image.width and 0 <= y < image.height:
                # Distant stars are smaller than closer stars
                size = (1 - star.z / star.MAX_DEPTH) * 4
                draw.rectangle((x, y, x + size, y + size), fill="white")

        return image
