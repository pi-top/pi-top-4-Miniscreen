import logging
from threading import Thread
from time import sleep
from typing import Callable

from ..state import Speeds
from ..types import Coordinate
from .marquee_text_hotspot import Hotspot as MarqueeHotspotBase

logger = logging.getLogger(__name__)


class Hotspot(MarqueeHotspotBase):
    DELTA_PX = 2

    def __init__(
        self,
        size: Coordinate,
        text: Callable[[], str],
        font=None,
        font_size: int = 20,
        interval: float = Speeds.MARQUEE.value,
        update_interval: float = 0.5,
    ):
        self.text_func = text
        super().__init__(
            size=size,
            text=self.text_func(),
            font=font,
            font_size=font_size,
            interval=interval,
        )
        self.update_interval = update_interval

        def _update_text():
            while True:
                self._wait_until_active()
                self.text = self.text_func()

                sleep(self.update_interval)

        self.thread = Thread(target=_update_text, args=(), daemon=True)

    def start(self):
        super().start()
        self.thread.start()
