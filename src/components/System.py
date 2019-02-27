from components.helpers import RequestServer
from ptcommon.logger import PTLogger
from os import uname


_device = None

_, _, _, _, machine = uname()

def is_pi():
    return machine == "armv7l"


def take_control_of_oled():
    global got_pi_control
    got_pi_control = RequestServer.take_control_of_oled()
    PTLogger.info("Pi has control of OLED? " + str(got_pi_control))


def setup_pi_and_get_device():
    take_control_of_oled()
    import RPi.GPIO as GPIO

    # Suppress warning in Luma serial class
    GPIO.setwarnings(False)

    from luma.core.interface.serial import spi

    spi_serial_iface = spi(
        port=1,
        device=0,
        bus_speed_hz=8000000,
        cs_high=False,
        transfer_size=4096,
        gpio_DC=17,
        gpio_RST=27,
        gpio=None,
    )
    from luma.oled.device import sh1106

    return sh1106(spi_serial_iface)


def setup_debug_and_get_device():
    from components.helpers.ButtonPressHelper import ButtonPressHelper

    ButtonPressHelper.init()
    from luma.emulator.device import pygame

    return pygame(
        display="pygame", height=64, mode="1", scale=4, transform="identity", width=128
    )


def setup_and_get_device():
    global _device
    if _device is None:
        if is_pi():
            _device = setup_pi_and_get_device()
        else:
            _device = setup_debug_and_get_device()

    return _device


got_pi_control = False
device = setup_and_get_device()
