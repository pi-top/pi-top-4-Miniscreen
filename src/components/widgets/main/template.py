#!/usr/bin/env python

from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseStaticHotspot


def page(title="Title"):
    def render(draw, width, height):
        margin = 3
        title_text(draw, margin, width, text=title)

    return render


class StaticHotspot(BaseStaticHotspot):
    def __init__(self, width, height, render_func):
        super(StaticHotspot, self).__init__(width, height, render_func)
