from time import time
from luma.core.virtual import (
    hotspot,
    snapshot
)


class BaseStaticHotspot(hotspot):
    def __init__(self, width, height, render_func):
        super(BaseStaticHotspot, self).__init__(width, height)
        self.redraw = True

        if callable(render_func):
            self._render = render_func
        else:
            raise Exception("Render function is not callable")

    def should_redraw(self):
        # TODO: Find out why this is constantly going true again
        return self.redraw

    def update(self, draw):
        if self._render is not None and self.redraw is True:
            self._render(draw, self.width, self.height)
            self.redraw = False


class BaseSnapshot(snapshot):
    def __init__(self, width, height, interval, render_func):
        super(BaseSnapshot, self).__init__(width, height, interval)
        self._interval = interval
        self._last_updated = 0
        if callable(render_func):
            self._render = render_func
        else:
            raise Exception("Render function is not callable")

    def update_last_updated(self):
        self._last_updated = time()

    def should_redraw(self):
        return time() - self._last_updated > self._interval

    def update(self, draw):
        if self._render is not None:
            self._render(draw, self.width, self.height)

        self.update_last_updated()
