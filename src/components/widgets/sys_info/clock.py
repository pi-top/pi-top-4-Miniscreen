# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import math
import datetime

from components.widgets.common_functions import title_text, draw_text
from components.widgets.common.base_widget_hotspot import BaseHotspot


def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)


def digital(draw, width, height):
    margin = 3

    now = datetime.datetime.now()
    today_date = now.strftime("%d %b %y")
    current_time = now.strftime("%H:%m:%S")

    title_text(draw, margin, width, today_date)
    draw_text(draw, xy=(margin + 10, 20), text=current_time)


def analog(draw, width, height):
    now = datetime.datetime.now()
    today_date = now.strftime("%d %b %y")

    y_offset = 16
    margin = 3

    cx = width / 2
    cy = y_offset + ((height - y_offset - margin) / 2)

    left = (width - (min(height, 64) - y_offset - margin)) / 2
    right = width - left
    radius = (right - left) / 2
    top = cy - radius
    bottom = cy + radius

    hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
    hrs = posn(hrs_angle, radius - 8)

    min_angle = 270 + (6 * now.minute)
    mins = posn(min_angle, radius - 3)

    sec_angle = 270 + (6 * now.second)
    secs = posn(sec_angle, radius - 3)

    draw.ellipse((left, top, right, bottom), outline="white")
    draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
    draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
    draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
    draw.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill="white", outline="white")
    title_text(draw, margin, width, today_date)


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        clock = analog if height >= 64 else digital
        clock(draw, width, height)
