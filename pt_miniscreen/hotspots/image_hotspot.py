import logging

import PIL.Image

from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(self, interval, size, mode, image_path, xy=None):
        super().__init__(interval, size, mode)
        self.xy = xy
        self.image = None
        self.image_path = image_path

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
            if self.xy is None:
                self.xy = (
                    self.size[0] / 2 - self.image.width / 2,
                    self.size[1] / 2 - self.image.height / 2,
                )
        except Exception as e:
            logger.warning(f"Couldn't open image {path} : {e}")
            raise
