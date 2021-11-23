import logging

import PIL.Image

from ..state import Speeds
from .base import Hotspot as HotspotBase

logger = logging.getLogger(__name__)


class Hotspot(HotspotBase):
    def __init__(
        self, size, image_path, xy=None, interval=Speeds.DYNAMIC_PAGE_REDRAW.value
    ):
        super().__init__(interval=interval, size=size)

        if xy is None:
            xy = (0, 0)

        self.xy = xy
        self._im = None
        self.image_path = image_path
        self._frame_no = 0
        self.loop = True
        self.playback_speed = 1.0

    def render(self, image):
        if not self._im:
            return

        if self._im.is_animated:
            if self._frame_no + 1 < self._im.n_frames:
                self._frame_no += 1
            elif self.loop:
                self._frame_no = 0

        self._im.seek(self._frame_no)

        if self._im.is_animated:
            embedded_frame_speed_s = float(self._im.info["duration"] / 1000)
            self.interval = float(embedded_frame_speed_s / self.playback_speed)

        PIL.ImageDraw.Draw(image).bitmap(
            xy=self.xy,
            bitmap=self._im.convert("1"),
            fill="white",
        )

    @property
    def image(self):
        return self._im

    @property
    def image_path(self):
        return self._im_path

    @image_path.setter
    def image_path(self, path):
        self._im_path = path
        self._setup_image()

    def _setup_image(self):
        if self.image_path is None:
            return
        try:
            self._im = PIL.Image.open(self.image_path).convert("1")
        except Exception as e:
            logger.warning(f"Couldn't open image {self.image_path} : {e}")
            raise
