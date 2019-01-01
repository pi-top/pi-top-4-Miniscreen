#!/usr/bin/env python

from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseStaticHotspot


class StaticHotspot(BaseStaticHotspot):
    def __init__(self, width, height, **data):
        super(StaticHotspot, self).__init__(width, height, self.render)

        for key, value in data.items():
            if key == "title":
                self.title = value

    def render(self, draw, width, height):
        margin = 3
        title_text(draw, margin, width, text=self.title)