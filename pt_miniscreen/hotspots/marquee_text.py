import logging
from multiprocessing import Event
from threading import Thread
from time import sleep

from pt_miniscreen.generators.scroll import carousel

from .text import TextHotspot

logger = logging.getLogger(__name__)


class MarqueeTextHotspot(TextHotspot):
    width = 0

    def __init__(
        self,
        step=2,
        step_time=0.1,
        vertical_align="bottom",  # use bottom to match previous impl
        initial_state={},
        **kwargs
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "offset": 0,
                "step": step,
                "vertical_align": vertical_align,
                "step_time": step_time,
                "wrap": False,
                **initial_state,
            },
        )

        self._stop_scroll_event = None

    @property
    def needs_scrolling(self) -> bool:
        text_size = self.get_text_size(self.state["text"], self.state["font"])
        return self.width < text_size[0]

    @property
    def scrolling(self) -> bool:
        return self._stop_scroll_event and not self._stop_scroll_event.is_set()

    def _start_scrolling(self):
        if not self.scrolling:
            self._stop_scroll_event = Event()
            Thread(
                target=self._scroll, args=[self._stop_scroll_event], daemon=True
            ).start()

    def _scroll(self, stop_event):
        text_size = self.get_text_size(self.state["text"], self.state["font"])
        scroll_len = min(text_size[0] - self.width, 0)

        for offset in carousel(max_value=scroll_len, resolution=self.state["step"]):
            sleep(self.state["step_time"])
            if stop_event.is_set():
                return

            self.state.update({"offset": offset})

    def cleanup(self):
        if self._stop_scroll_event:
            self._stop_scroll_event.set()

    def on_state_change(self, previous_state):
        if previous_state["text"] == self.state["text"]:
            return

        if not self.scrolling and self.needs_scrolling:
            self._start_scrolling()

        if self.scrolling and not self.needs_scrolling:
            self._stop_scroll_event.set()

    def render(self, image):
        image.paste(super().render(image), (self.state["offset"], 0))
        return image
