#!/usr/bin/env python

import time
from luma.core.virtual import hotspot
from hotspot.common import title_text

def render(draw, width, height):
    title_text(draw, height/3, width, "Projects")

class Projects(hotspot):

    def __init__(self, width, height, interval):
        super(Projects, self).__init__(width, height)
        self._interval = interval
        self._last_updated = 0

    def should_redraw(self):
        return time.time() - self._last_updated > self._interval

    def update(self, draw):
        render(draw, self.width, self.height)
        self._last_updated = time.time()
