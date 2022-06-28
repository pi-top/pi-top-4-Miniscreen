import logging
from threading import Event, Thread
from time import sleep

from PIL import Image

from ..utils import carousel
from .text import Text

logger = logging.getLogger(__name__)


class MarqueeText(Text):
    def cleanup(self):
        if self._stop_scroll_event:
            self._stop_scroll_event.set()

    def __init__(
        self,
        step=1,
        step_time=0.1,
        initial_state={},
        wrap=None,  # take wrap out of kwargs
        bounce_pause_time=1,
        **kwargs
    ):
        super().__init__(
            **kwargs,
            wrap=False,
            initial_state={
                **initial_state,
                "offset": 0,
                "step": step,
                "step_time": step_time,
                "bounce_pause_time": bounce_pause_time,
            },
        )

        self._stop_scroll_event = None

    @property
    def needs_scrolling(self) -> bool:
        text_size = self.get_text_size(self.state["text"], self.state["font"])
        return self.width is not None and self.width < text_size[0]

    @property
    def scrolling(self) -> bool:
        return self._stop_scroll_event and not self._stop_scroll_event.is_set()

    def _start_scrolling(self):
        if not self.scrolling:
            self._stop_scroll_event = Event()
            Thread(
                target=self._scroll, args=[self._stop_scroll_event], daemon=True
            ).start()

    def _restart_scrolling(self):
        if self._stop_scroll_event:
            self._stop_scroll_event.set()

        self.state.update({"offset": 0})
        self._start_scrolling()

    def _scroll(self, stop_event):
        text_size = self.get_text_size(self.state["text"], self.state["font"])
        scroll_len = max(text_size[0] - self.width, 0)

        for offset in carousel(scroll_len, step=self.state["step"]):
            self.active_event.wait()

            sleep(self.state["step_time"])

            if stop_event.is_set():
                return

            self.state.update({"offset": -offset})

            if offset in (1, scroll_len):
                sleep(self.state["bounce_pause_time"])

    def on_state_change(self, prev_state):
        # restart scrolling to recreate carousel with new text size if needed
        if (
            self.state["text"] != prev_state["text"]
            or self.state["font"] != prev_state["font"]
        ):
            if self.needs_scrolling:
                self._restart_scrolling()

    def render(self, image):
        if not self.scrolling and self.needs_scrolling:
            self._start_scrolling()

        if self.scrolling and not self.needs_scrolling:
            self._stop_scroll_event.set()

        text_size = self.get_text_size(self.state["text"], self.state["font"])
        offset = self.state["offset"] if self.needs_scrolling else 0

        image.paste(
            super().render(Image.new("1", size=(text_size[0], image.height))),
            (offset, 0),
        )
        return image
