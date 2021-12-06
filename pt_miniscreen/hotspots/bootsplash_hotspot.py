import logging
from configparser import ConfigParser
from os import path

from ..event import AppEvent, post_event
from ..hotspots.image_hotspot import Hotspot as ImageHotspot
from ..utils import get_image_file_path

logger = logging.getLogger(__name__)


class BootsplashHotspot(ImageHotspot):
    def __init__(self, size):
        # image_path
        config_file = "/etc/pt-miniscreen/settings.ini"

        image_path = get_image_file_path("startup/pi-top_startup.gif")

        if path.exists(config_file):
            config = ConfigParser()
            config.read(config_file)
            try:
                image_path = config.get("Bootsplash", "Path")
            except Exception:
                pass

        super().__init__(size, image_path, loop=False)

    def render(self, image):
        if self._im.is_animated and not self.loop:
            if self._frame_no + 1 == self._im.n_frames:
                return image

        render_image = super().render(image)

        # Stop bootsplash on final frame
        if self._im.is_animated and not self.loop:
            if self._frame_no + 1 == self._im.n_frames:
                post_event(AppEvent.STOP_BOOTSPLASH)

        return render_image
