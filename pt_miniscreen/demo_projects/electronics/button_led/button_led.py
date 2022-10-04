from time import sleep

from pitop.pma import LED, Button
from pitop.miniscreen import Miniscreen

miniscreen = Miniscreen()
button = Button("D1")
led = LED("D2")

button.when_pressed = led.on
button.when_released = led.off

miniscreen.display_multiline_text(
    "Connect Button to D1 and LED to D2. Press Button to toggle LED."
)

i = 0
while i < 5:
    sleep(1)
    i += 1
