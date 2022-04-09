import logging
import sys
from signal import pause

from pt_miniscreen.asteroids.app import App

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = App()
app.start()
pause()
