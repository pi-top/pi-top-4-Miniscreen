from time import sleep

from pitop.pma import LED
from pitop.miniscreen import Miniscreen

led = LED("D2")
miniscreen = Miniscreen()

miniscreen.display_multiline_text("Connect a LED to D2.")
sleep(3)

for i in range(5):
    led.toggle()
    message = f"LED is{'' if led.is_lit else ' not'} lit"
    miniscreen.display_multiline_text(message)
    sleep(1)
