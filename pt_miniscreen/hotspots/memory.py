import psutil
from pitop.common.formatting import bytes2human

from .templates.text import Hotspot as TextHotspot


class Hotspot(TextHotspot):
    def __init__(
        self,
        size,
        text,
        interval=5,
    ):
        super().__init__(
            size,
            text,
            interval=interval,
        )

    @property
    def text(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

        return f"""Memory
        Used: {"{0:0.1f}%".format(mem_used_pct)}
        Phys: {bytes2human(mem.used)}
        Swap: {bytes2human(swap.used)}
        """

    @text.setter
    def text(self, value_or_callback):
        # Nothing to do
        pass
