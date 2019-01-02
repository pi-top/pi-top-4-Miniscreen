from time import time
from luma.core.virtual import snapshot
try:
    monotonic = time.monotonic
except AttributeError:  # pragma: no cover
    from monotonic import monotonic


class BaseHotspot(snapshot):
    """
    A base class which has properties of luma hotspot and snapshot, as appropriate
    """
    def __init__(self, width, height, interval=0.0, draw_fn=None, **kwargs):
        # Get from data?
        super(BaseHotspot, self).__init__(width, height, draw_fn=draw_fn, interval=interval)

    def should_redraw(self):
        """
        Only requests a redraw after ``interval`` seconds have elapsed.
        """
        if self.interval <= 0.0:
            return True
        else:
            return monotonic() - self.last_updated > self.interval
