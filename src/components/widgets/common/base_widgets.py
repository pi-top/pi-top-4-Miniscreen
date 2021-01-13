from time import time
from luma.core.virtual import (
    hotspot,
    snapshot,
)

try:
    monotonic = time.monotonic
except AttributeError:  # pragma: no cover
    from monotonic import monotonic


class BaseSnapshot(snapshot):
    def __init__(self, width, height, interval=0.5, draw_fn=None, **kwargs):
        super(BaseSnapshot, self).__init__(
            width=width,
            height=height,
            draw_fn=draw_fn,
            interval=interval
        )

    def reset(self):
        pass

    def should_redraw(self):
        """
        Only requests a redraw after ``interval`` seconds have elapsed.
        """
        if self.interval <= 0.0:
            return True
        else:
            return monotonic() - self.last_updated > self.interval


class BaseHotspot(hotspot):
    def __init__(self, width, height, draw_fn=None, **kwargs):
        super(BaseHotspot, self).__init__(
            width=width,
            height=height,
            draw_fn=draw_fn
        )

    def reset(self):
        pass

    def should_redraw(self):
        return False
