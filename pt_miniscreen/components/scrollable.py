from time import sleep
from threading import Thread
import logging
import time
from pt_miniscreen.core.component import Component
from pt_miniscreen.utils import VIEWPORT_HEIGHT


logger = logging.getLogger(__name__)


class SpeedRamp:
    TOP_SPEED = 20
    BASE_SPEED = 5
    ACCELERATION = 4
    ramp = False
    direction = 1

    def __init__(self) -> None:
        self.speed = self.BASE_SPEED * self.direction

    def forwards(self):
        self.direction = abs(self.direction)

    def backwards(self):
        self.direction = -1 * abs(self.direction)

    def stop(self):
        self.ramp = False
        self.speed = 0

    def start(self):
        self.ramp = True
        Thread(target=self.run, daemon=True).start()

    def run(self):
        elapsed = 0
        delta_t = 0.1

        self.speed = self.BASE_SPEED * self.direction

        while self.ramp:
            if elapsed > 1:
                self.speed += self.direction * self.ACCELERATION
                if self.speed >= self.TOP_SPEED:
                    self.ramp = False

            sleep(delta_t)
            elapsed += delta_t


class Scrollable(Component):
    def __init__(self, image, initial_state={}, **kwargs) -> None:
        super().__init__(
            initial_state={
                "image": image,
                "y_pos": 0,
                "speed": 0,
                "start_time": 0,
                **initial_state,
            },
            **kwargs
        )
        self.scroll_speed_tracker = SpeedRamp()
        self.create_interval(self.update_state, timeout=0.05)

    def update_state(self):
        speed = self.scroll_speed_tracker.speed
        now = 0
        if self.state["start_time"] > 0:
            now = time.time()

        dt = now - self.state["start_time"]
        if 0 < dt < 1:
            dt = 1

        y_pos = self.state["y_pos"] + speed * int(dt)
        if y_pos + VIEWPORT_HEIGHT > self.state["image"].height:
            y_pos = self.state["image"].height - VIEWPORT_HEIGHT
        if y_pos < 0:
            y_pos = 0

        self.state.update({"y_pos": y_pos, "speed": speed})

    def scroll_down(self):
        self.scroll_speed_tracker.forwards()
        self.state["start_time"] = time.time()
        self.scroll_speed_tracker.start()

    def scroll_up(self):
        self.scroll_speed_tracker.backwards()
        self.state["start_time"] = time.time()
        self.scroll_speed_tracker.start()

    def stop_scrolling(self):
        self.scroll_speed_tracker.stop()
        self.state.update({"start_time": 0})

    def render(self, image):
        return self.state["image"].crop(
            (0, self.state["y_pos"], image.width, self.state["y_pos"] + image.height)
        )
