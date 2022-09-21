from time import sleep

from pitop import LED, Button


button = Button("D1")
led = LED("D2")

button.when_pressed = led.on
button.when_released = led.off

i = 0
while i < 5:
    sleep(1)
    i += 1
