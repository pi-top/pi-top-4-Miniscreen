from time import sleep

from pitop import LED


led = LED("D2")

for i in range(5):
    led.toggle()
    print(f"LED is{'' if led.is_lit else 'not'} lit")
    sleep(1)
