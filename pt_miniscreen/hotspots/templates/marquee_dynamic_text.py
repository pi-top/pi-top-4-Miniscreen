import logging
from threading import Event, Thread
from time import sleep
from typing import Callable

from ...state import Speeds
from ...types import Coordinate
from .marquee_text import Hotspot as MarqueeHotspotBase

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
        self._text_update_stop_event = Event()

        def _update_text():
            while not self._text_update_stop_event.is_set():
                if self.active:
                    self.text = self.text_func()

                sleep(self.update_interval)

        self.thread = Thread(target=_update_text, daemon=True)

    def start(self):
        super().start()
        self.thread.start()

    def cleanup(self):
        self._text_update_stop_event.set()
        super().cleanup()
