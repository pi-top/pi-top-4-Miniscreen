from threading import Event
from time import sleep


class SleepMocker:
    def __init__(self) -> None:
        self.sleep_event = Event()

    def sleep(self, time):
        print(f"sleeping for {time}...")
        self.sleep_event.clear()
        self.sleep_event.wait()

    def wait_until_next_call(self, sleep_mock):
        current = sleep_mock.call_count
        self.sleep_event.set()
        while sleep_mock.call_count == current:
            sleep(0.01)
