import datetime
import logging
from os import environ
from pathlib import Path
from threading import Event

from PIL import Image

from pitop.common.ptdm import Message, PTDMSubscribeClient


logger = logging.getLogger(__name__)


class App:
    def __init__(self, miniscreen=None, Root=None):
        assert miniscreen is not None
        assert Root is not None
        self.miniscreen = miniscreen
        self.Root = Root

        self._stop_event = Event()
        self.saved_cache_frame_no = 0
        self.timestamp = (
            str(datetime.datetime.now())
            .split(".")[0]
            .replace(" ", "_")
            .replace(":", "-")
        )

        def reset_miniscreen() -> None:
            logger.info("pi-topd is ready - resetting miniscreen")
            try:
                miniscreen.reset()
                self.display()
            except RuntimeError as e:
                logger.error(f"Error resetting miniscreen: {e}")

                # stop the app so that systemd can restart the service
                self.stop(e)

        self._ptdm_subscribe_client = PTDMSubscribeClient()
        self._ptdm_subscribe_client.initialise(
            {Message.PUB_PITOPD_READY: reset_miniscreen}
        )
        self._ptdm_subscribe_client.start_listening()

    def start(self):
        self.root = self.Root(on_rerender=self.display)
        self.root._set_active(True)
        self.display()

    def stop(self, error=None):
        self.root._cleanup()
        self.root = None
        self._stop_error = error
        self._stop_event.set()
        self._ptdm_subscribe_client.stop_listening()

    def wait_for_stop(self) -> None:
        self._stop_event.wait()
        error = getattr(self, "_stop_error", None)
        if isinstance(error, Exception):
            raise error

    # This should use `miniscreen.display_image` but that method attempts to
    # import opencv when it's called. We can catch the raised error but cannot
    # prevent the module search. This produces overhead when display is called
    # frequently, which is expected. It's worth noting the import is not cached
    # since the module was not found so the search happens every import attempt
    def display(self):
        image = self.root.render(Image.new("1", self.miniscreen.size))

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
        self.miniscreen.device.display(image)
