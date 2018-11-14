from os import uname


_device = None


def is_pi():
    _, _, _, _, machine = uname()
    return machine == "armv7l"


def setup_pi_and_get_device():
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
        gpio=None
    )
    from luma.oled.device import sh1106
    return sh1106(spi_serial_iface)


def setup_debug_and_get_device():
    from components.helpers.ButtonPressHelper import ButtonPressHelper
    ButtonPressHelper.init()
    from luma.emulator.device import pygame
    return pygame(
        display='pygame',
        height=64,
        mode='1',
        scale=4,
        transform='identity',
        width=128
    )


def setup_and_get_device():
    global _device
    if _device is None:
        if is_pi():
            _device = setup_pi_and_get_device()
        else:
            _device = setup_debug_and_get_device()

    return _device


device = setup_and_get_device()
