#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

from demo_opts import get_device
from luma.core.virtual import viewport, snapshot

from hotspot import uptime, batt_level


def main():
    utime = snapshot(device.width, device.height, uptime.render, interval=1.0)
    battery = snapshot(device.width, device.height, batt_level.render, interval=1.0)

    virtual = viewport(device, width=device.width, height=device.height)
    virtual.add_hotspot(battery, (0, 0))

    while True:
        virtual.set_position((0, 0))


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass