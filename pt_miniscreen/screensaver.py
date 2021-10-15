from random import randrange

from PIL import Image, ImageDraw


class Screensaver:
    SCREENSAVER_MAX_DEPTH = 32
    SCREENSAVER_MAX_NO_OF_STARS = 512

    def __init__(self, miniscreen):
        self.mode = miniscreen.mode
        self.size = miniscreen.size

        self.screensaver_stars = [
            [
                randrange(-25, 25),
                randrange(-25, 25),
                randrange(1, self.SCREENSAVER_MAX_DEPTH),
            ]
            for i in range(self.SCREENSAVER_MAX_NO_OF_STARS)
        ]

    @property
    def image(self):
        # Adapted from https://github.com/rm-hull/luma.examples/blob/master/examples/starfield.py

        origin_x = self.miniscreen.size[0] // 2
        origin_y = self.miniscreen.size[1] // 2

        image = Image.new(self.miniscreen.mode, self.miniscreen.size)

        draw = ImageDraw.Draw(image)

        for star in self.screensaver_stars:
            star[2] -= 0.19

            if star[2] <= 0:
                star[0] = randrange(-25, 25)
                star[1] = randrange(-25, 25)
                star[2] = self.SCREENSAVER_MAX_DEPTH

            k = 128.0 / star[2]
            x = int(star[0] * k + origin_x)
            y = int(star[1] * k + origin_y)

            if 0 <= x < self.miniscreen.size[0] and 0 <= y < self.miniscreen.size[1]:
                size = (1 - float(star[2]) / self.SCREENSAVER_MAX_DEPTH) * 4
                draw.rectangle((x, y, x + size, y + size), fill="white")

        return image
