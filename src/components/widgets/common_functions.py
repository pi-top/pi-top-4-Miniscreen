#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import ImageFont
import os.path
from datetime import datetime
import psutil
import subprocess
from fractions import Fraction
from os import getloadavg


tiny_font = ImageFont.truetype(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "fonts", "FreePixel.ttf")), 10)


# def bytes2human(n):
#     """
#     >>> bytes2human(10000)
#     '9K'
#     >>> bytes2human(100001221)
#     '95M'
#     """
#     symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
#     prefix = {}
#     for i, s in enumerate(symbols):
#         prefix[s] = 1 << (i + 1) * 10
#     for s in reversed(symbols):
#         if n >= prefix[s]:
#             value = int(float(n) / prefix[s])
#             return '%s%s' % (value, s)
#     return "%sB" % n


def bytes2human(n, fmt="{0:0.2f}"):
    symbols = [
        ('YB', 2 ** 80),
        ('ZB', 2 ** 70),
        ('EB', 2 ** 60),
        ('PB', 2 ** 50),
        ('TB', 2 ** 40),
        ('GB', 2 ** 30),
        ('MB', 2 ** 20),
        ('KB', 2 ** 10),
        ('B', 2 ** 0)
    ]

    for suffix, v in symbols:
        if n >= v:
            value = float(n) / v
            return fmt.format(value) + suffix
    return "{0}B".format(n)


def right_text(draw, y, width, margin, text):
    x = width - margin - draw.textsize(text, font=tiny_font)[0]
    draw.text((x, y), text=text, font=tiny_font, fill="white")


def title_text(draw, y, width, text):
    x = (width - draw.textsize(text)[0]) / 2
    draw.text((x, y), text=text, fill="yellow")


def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])


def cpu_percentage():
    av1, av2, av3 = getloadavg()
    average = sum([av1, av2, av3])/float(3) * 100
    return str("%.1f" % average) + "%"


def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)


def network_rate(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))


def network_strength(iface):
    strength = -1
    try:
        response_str = str(subprocess.check_output(["iwconfig", iface]).decode("utf-8"))
        response_lines = response_str.splitlines()
        for line in response_lines:
            if "Link Quality" in line:
                strength_str = line.lstrip(" ").lstrip("Link Quality=").split(" ")[0]
                strength = int(Fraction(strength_str) * 100)
                break
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return str(strength) + "%"


# TODO: Get from same place as batt_level widget - should there be a common Python interface for this data?
def get_battery():
    try:
        battery_level = str(subprocess.check_output(["pt-battery", "-c"]).decode("utf-8")).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        battery_level = "TEST"

    return str(battery_level + "%")


def get_temperature():
    try:
        battery_level = str(subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")).strip()\
                            .lstrip("temp=")\
                            .rstrip("'C\n")
    except (FileNotFoundError, subprocess.CalledProcessError):
        battery_level = "TEST"

    return str(battery_level + u'\N{DEGREE SIGN}' + "C")


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
