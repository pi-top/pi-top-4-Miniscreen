from os import (
    getloadavg,
    path
)
from datetime import datetime
import psutil
import subprocess
from fractions import Fraction
from PIL import Image, ImageFont

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
    cmd = subprocess.Popen('iwconfig %s' % iface, shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "Link Quality" in line:
          strength_str = line.lstrip(" ").lstrip("Link Quality=").split(" ")[0]
          strength = int(Fraction(strength_str) * 100)
#          return "Wi-Fi Strength:  " + str(strength) + "%"
          return str(strength) + "%"
    return ""


def get_battery():
    cmd = subprocess.Popen('pt-battery -c', shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        return str(line).rstrip("\n") + "%"

    return "lol%"


def get_temperature():
    cmd = subprocess.Popen('vcgencmd measure_temp', shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        return str(line).lstrip("temp=").rstrip("'C\n") + u'\N{DEGREE SIGN}' + "C"

    return "lol degrees"


font = ImageFont.truetype(
    path.abspath(path.join(path.dirname(__file__), '..', '..', '..', 'fonts', 'C&C Red Alert [INET].ttf')),
    size=12)


def render(draw, width, height):
    draw.text(xy=(0 * width/4, 0 * height/4), text=get_battery(), font=font)
    img_bitmap = Image.open("widgets/sys_info/assets/battery.png").convert("RGBA")
    draw.bitmap((1 * width/4, 0 * height/4), img_bitmap, fill="white")

    draw.text(xy=(2 * width/4, 0 * height/4), text=network_strength('wlan0'), font=font)
    img_bitmap = Image.open("widgets/sys_info/assets/wifi_icon.png").convert("RGBA")
    draw.bitmap((3 * width/4, 0 * height/4), img_bitmap, fill="white")

    draw.text(xy=(0 * width/4, 2 * height/4), text=cpu_percentage(), font=font)
    img_bitmap = Image.open("widgets/sys_info/assets/cpu.png").convert("RGBA")
    draw.bitmap((1 * width/4, 2 * height/4), img_bitmap, fill="white")

    draw.text(xy=(2 * width/4, 2 * height/4), text=get_temperature(), font=font)
    img_bitmap = Image.open("widgets/sys_info/assets/thermometer.png").convert("RGBA")
    draw.bitmap((3 * width/4, 2 * height/4), img_bitmap, fill="white")
