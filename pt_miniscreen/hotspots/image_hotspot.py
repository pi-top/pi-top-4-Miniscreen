import logging

import PIL.Image

from .base import HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode, image_path, xy=None):
        super().__init__(interval, size, mode)
        self.image = None
        self.image_path = image_path

        if xy is None:
            xy = (0, 0)
        self.xy = xy

    def render(self, image):
        if self.image:
            PIL.ImageDraw.Draw(image).bitmap(
                xy=self.xy,
                bitmap=self.image.convert(self.mode),
                fill="white",
            )

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, path):
        self._image_path = path
        if path is None:
            return
        try:
            self.image = PIL.Image.open(path)
        except Exception as e:
            logger.warning(f"Couldn't open image {path} : {e}")
            raise
