#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import subprocess
from components.widgets.common_functions import (
    bytes2human,
    right_text,
    title_text,
    tiny_font
)
from components.widgets.common.base_widget_hotspot import BaseSnapshot


def get_network_id():
    try:
        network_id = str(subprocess.check_output(["iwgetid", "-r"]).decode("utf-8")).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        network_id = "TEST"

    return network_id


def get_internal_ip():
    try:
        internal_ip = str(subprocess.check_output(["hostname", "-I"]).decode("utf-8")).split(" ")[0].strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        internal_ip = "TEST"

    return internal_ip


def get_ssh_enabled_state():
    try:
        ssh_enabled_state = str(subprocess.check_output(["systemctl", "is-enabled", "ssh"]).decode("utf-8")).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        ssh_enabled_state = "TEST"

    return ssh_enabled_state


def render(draw, width, height):
    margin = 3
    title_text(draw, margin, width, text="Wi-Fi Info")
    draw.text((margin, 20), text=str("SSID: " + get_network_id()), font=tiny_font, fill="white")
    draw.text((margin, 35), text=str("  IP: " + get_internal_ip()), font=tiny_font, fill="white")
    draw.text((margin, 50), text=str(" SSH: " + get_ssh_enabled_state()), font=tiny_font, fill="white")


class Snapshot(BaseSnapshot):
    def __init__(self, width, height, interval, render_func, **data):
        super(Snapshot, self).__init__(width, height, interval, render)
