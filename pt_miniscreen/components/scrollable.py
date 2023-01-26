from time import sleep
from threading import Thread
import time
from pt_miniscreen.core.component import Component
import logging


logger = logging.getLogger(__name__)


class SpeedRamp:
    speed = 20
    ramp = False
    top_speed = 2000
    delta = 10

    def forwards(self):
        self.delta = abs(self.delta)

    def backwards(self):
        self.delta = -1 * abs(self.delta)

    def stop(self):
        self.ramp = False
        self.speed = 0

    def start(self):
        self.ramp = True
        Thread(target=self.run, daemon=True).start()

    def run(self):
        i = 1
        while self.ramp:
            self.speed += self.delta * i
            i += 1
            if self.speed >= self.top_speed:
                self.ramp = False
            sleep(0.2)


class Scrollable(Component):
    def __init__(self, image, **kwargs) -> None:
        super().__init__(
            initial_state={"y_pos": 0, "speed": 0, "start_time": 0}, **kwargs
        )
        self.image = image
        self.scroll_speed_tracker = SpeedRamp()
        self.create_interval(self.update_state, timeout=0.2)

    def update_state(self):
        speed = self.scroll_speed_tracker.speed
        now = 0
        if self.state["start_time"] > 0:
            now = time.time()

        y_pos = self.state["y_pos"] + speed * (now - self.state["start_time"])
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
        top_y = self.state["y_pos"]
        if top_y + image.height > self.image.height:
            top_y = self.image.height - image.height

        return self.image.crop((0, top_y, image.width, top_y + image.height))
