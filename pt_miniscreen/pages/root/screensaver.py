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
        self.create_interval(self.star_array.update_positions, timeout=0.05)

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

    @property
    def position(self):
        return (self.x, self.y, self.z)

    @position.setter
    def position(self, value):
        self.x, self.y, self.z = value

    def move(self):
        x = self.x
        y = self.y
        z = self.z - self.DELTA_Z

        # Star has moved 'past the display'
        if z <= 0:
            # Reposition far away from the screen (Z=max_depth)
            # with random X and Y coordinates
            x = randrange(-25, 25)
            y = randrange(-25, 25)
            z = self.MAX_DEPTH

        self.position = (x, y, z)
        return (x, y, z)


class StarArray(Component):
    SCREENSAVER_MAX_DEPTH = 32

    def __init__(self, star_number, **kwargs):
        self.stars = [Star() for _ in range(star_number)]

        super().__init__(
            **kwargs,
            initial_state={"positions": [star.position for star in self.stars]}
        )

    def update_positions(self):
        self.state.update({"positions": [star.move() for star in self.stars]})

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
