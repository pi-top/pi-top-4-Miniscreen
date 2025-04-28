import datetime
import logging
from os import environ
from pathlib import Path
from threading import Event

from PIL import Image

logger = logging.getLogger(__name__)


class App:
    def __init__(self, display=None, Root=None, size=(128, 64), image_mode="1"):
        assert display is not None
        assert Root is not None
        self._display = display
        self.Root = Root

        self.image_mode = image_mode
        self.size = size

        self._stop_event = Event()
        self.saved_cache_frame_no = 0
        self.timestamp = (
            str(datetime.datetime.now())
            .split(".")[0]
            .replace(" ", "_")
            .replace(":", "-")
        )

    def start(self):
        self.root = self.Root(on_rerender=self.display)
        self.root._set_active(True)
        self.display()

    def stop(self, error=None):
        if self.root:
            self.root._cleanup()
            self.root = None
        self._stop_error = error
        self._stop_event.set()

    def wait_for_stop(self) -> None:
        self._stop_event.wait()
        error = getattr(self, "_stop_error", None)
        if isinstance(error, Exception):
            raise error

    def display(self):
        image = self.root.render(Image.new(self.image_mode, self.size))

        # debug: print displayed image in terminal
        if environ.get("IMGCAT", "0") == "1":
            from imgcat import imgcat

            imgcat(image)

        # debug: store images in /tmp/pt-miniscreen
        if environ.get("SAVE_CACHE", "0") == "1":
            path = Path(f"/tmp/pt-miniscreen/{self.timestamp}")
            path.mkdir(parents=True, exist_ok=True)
            image.save(path / f"{str(self.saved_cache_frame_no).zfill(4)}.png")
            self.saved_cache_frame_no += 1

        logger.debug("Update display")
        self._display(image)
