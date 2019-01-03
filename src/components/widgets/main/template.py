#!/usr/bin/env python

from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.title = data.get("title")

    def render(self, draw, width, height):
        margin = 3
        title_text(draw, margin, width, text=self.title)
