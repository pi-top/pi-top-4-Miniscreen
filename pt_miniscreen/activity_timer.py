from time import perf_counter


class ActivityTimer:
    def __init__(self):
        self.last_active_time = perf_counter()

    def reset(self):
        self.last_active_time = perf_counter()

    @property
    def elapsed_time(self):
        return perf_counter() - self.last_active_time
