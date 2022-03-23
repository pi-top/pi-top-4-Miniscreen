import logging
import sys
from signal import pause
from threading import Thread

from pt_miniscreen.app import App

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = App()
Thread(target=app.start).start()
pause()
