from time import sleep

from pitop.pma import UltrasonicSensor
from pitop.miniscreen import Miniscreen


distance_sensor = UltrasonicSensor("D3", threshold_distance=0.2)
m = Miniscreen()

distance_sensor.when_in_range = lambda: m.display_text("in range")
distance_sensor.when_out_of_range = lambda: m.display_text("out of range")

i = 0.0
delta = 0.1
while i < 10:
    m.display_text(distance_sensor.distance)
    sleep(delta)
    i += delta
