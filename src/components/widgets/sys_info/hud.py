from os import (
    getloadavg,
    path
)
from datetime import datetime
import psutil
import subprocess
from fractions import Fraction
from PIL import (
    Image,
    ImageFont
)
from components.widgets.common.base_widget_hotspot import BaseSnapshot


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n


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


font = ImageFont.truetype(
    path.abspath(path.join(path.dirname(__file__), '..', '..', '..', 'fonts', 'C&C Red Alert [INET].ttf')),
    size=12)


# TODO: Fix images loading correctly
def render(draw, width, height):
    draw.text(xy=(0 * width/4, 0 * height/4), text=get_battery(), font=font, fill="white")
    img_path = path.abspath(path.join(path.dirname(__file__), 'assets', 'battery.png'))
    img_bitmap = Image.open(img_path).convert("RGBA")
    draw.bitmap(xy=(1 * width/4, 0 * height/4), bitmap=img_bitmap, fill="white")

    draw.text(xy=(2 * width/4, 0 * height/4), text=network_strength('wlan0'), font=font, fill="white")
    img_path = path.abspath(path.join(path.dirname(__file__), 'assets', 'wifi_icon.png'))
    img_bitmap = Image.open(img_path).convert("RGBA")
    draw.bitmap(xy=(3 * width/4, 0 * height/4), bitmap=img_bitmap, fill="white")

    draw.text(xy=(0 * width/4, 2 * height/4), text=cpu_percentage(), font=font, fill="white")
    img_path = path.abspath(path.join(path.dirname(__file__), 'assets', 'cpu.png'))
    img_bitmap = Image.open(img_path).convert("RGBA")
    draw.bitmap(xy=(1 * width/4, 2 * height/4), bitmap=img_bitmap, fill="white")

    draw.text(xy=(2 * width/4, 2 * height/4), text=get_temperature(), font=font, fill="white")
    img_path = path.abspath(path.join(path.dirname(__file__), 'assets', 'thermometer.png'))
    img_bitmap = Image.open(img_path).convert("RGBA")
    draw.bitmap(xy=(3 * width/4, 2 * height/4), bitmap=img_bitmap, fill="white")


class Snapshot(BaseSnapshot):
    def __init__(self, width, height, interval, render_func, **data):
        super(Snapshot, self).__init__(width, height, interval, render)
