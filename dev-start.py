import logging
import os
import sys
from signal import pause
from threading import Thread

from pt_miniscreen.app import App

os.environ["PYTHONUNBUFFERED"] = "1"
logging.getLogger("pitop.common").setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = App()
Thread(target=app.start).start()
pause()
