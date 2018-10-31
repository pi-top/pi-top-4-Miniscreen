from os import getloadavg
from datetime import datetime
import psutil
import subprocess
from fractions import Fraction

from os import sys, path
root = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(root)
import ptoled

ptoled.init()
ptoled.set_font_path(path.abspath(path.join(path.dirname(__file__),
                                     'fonts', 'C&C Red Alert [INET].ttf')))
ptoled.set_font_size(12)
ptoled.set_frame_rate(1)


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


def get_temperature():
    cmd = subprocess.Popen('vcgencmd measure_temp', shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        return str(line).lstrip("temp=").rstrip("'C\n") + u'\N{DEGREE SIGN}' + "C"


while True:
    ptoled.clear()
    

    # ptoled.text((0, 26), disk_usage('/'))
    # ptoled.text((0, 38), network_rate('wlan0'))

    ptoled.text((0 * ptoled.get_width()/4, 0 * ptoled.get_height()/4), get_battery())
    ptoled.image((1 * ptoled.get_width()/4, 0 * ptoled.get_height()/4), "battery.png")

    ptoled.text((2 * ptoled.get_width()/4, 0 * ptoled.get_height()/4), network_strength('wlan0'))
    ptoled.image((3 * ptoled.get_width()/4, 0 * ptoled.get_height()/4), "wifi_icon.png")


    ptoled.text((0 * ptoled.get_width()/4, 2 * ptoled.get_height()/4), cpu_percentage())
    ptoled.image((1 * ptoled.get_width()/4, 2 * ptoled.get_height()/4), "cpu.png")

    ptoled.text((2 * ptoled.get_width()/4, 2 * ptoled.get_height()/4), get_temperature())
    ptoled.image((3 * ptoled.get_width()/4, 2 * ptoled.get_height()/4), "thermometer.png")

    ptoled.draw()

