#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

from demo_opts import get_device
from luma.core.virtual import viewport, snapshot
import psutil

from hotspot import uptime, batt_level, cpu_load, network, date_time, project_template

def intersect(a, b):
    return list(set(a) & set(b))


def first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default


def main():
    # battery = snapshot(device.width, device.height, batt_level.render, interval=1.0)
    # network_ifs = psutil.net_if_stats().keys()
    # wlan = first(intersect(network_ifs, ["wlan0", "wl0"]), "wlan0")
    # wifi = snapshot(device.width, device.height, network.stats(wlan), interval=2.0)
    # date_time_widget = snapshot(device.width, device.height, date_time.render, interval=2.0)
    project_page = snapshot(device.width, device.height, project_template.project(title="Project Name", img_path="/home/choudhry/repos/release/python3-pt-oled-deb/src/assets/images/pi-top.png"), interval=2.0)

    virtual = viewport(device, width=device.width, height=device.height)
    virtual.add_hotspot(project_page, (0, 0))

    while True:
        virtual.set_position((0, 0))


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
