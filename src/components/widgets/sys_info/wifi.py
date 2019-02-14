#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from ptcommon.sys_info import (
    get_network_id,
    get_internal_ip,
    get_ssh_enabled_state
)
from components.widgets.common_functions import (
    right_text,
    title_text,
    tiny_font
)
from components.widgets.common.base_widget_hotspot import BaseHotspot


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, Hotspot.render)

    @staticmethod
    def render(draw, width, height):
        margin = 3
        title_text(draw, margin, width, text="Wi-Fi Info")
        draw.text((margin, 20), text=str("SSID: " + get_network_id()), font=tiny_font, fill="white")
        draw.text((margin, 35), text=str("  IP: " + get_internal_ip()), font=tiny_font, fill="white")
        draw.text((margin, 50), text=str(" SSH: " + get_ssh_enabled_state()), font=tiny_font, fill="white")
