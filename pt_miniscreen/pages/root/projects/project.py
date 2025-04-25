import atexit
import logging
import os
from queue import Queue
import shutil
from pathlib import Path
from shlex import split
from subprocess import PIPE, Popen
from time import sleep
from threading import Timer, Thread
from typing import Optional

from pitop.common.current_session_info import (
    get_first_display,
    get_user_using_first_display,
)
from pitop.common.switch_user import switch_user
from pitop.common.ptdm import Message, PTDMSubscribeClient
from pt_miniscreen.pages.root.projects.config import ProjectConfig
from pt_miniscreen.pages.root.projects.enums import ProjectExitCondition


logger = logging.getLogger(__name__)


class Project:
    def __init__(self, config: ProjectConfig) -> None:
        self.config: ProjectConfig = config
        self.subscribe_client: Optional[PTDMSubscribeClient] = None
        self.process: Optional[Popen] = None
        self.log_queue: Queue = Queue()
        atexit.register(self.cleanup)

    def _get_environment(self):
        env = os.environ.copy()

        if "PT_MINISCREEN_SYSTEM" in env:
            # Allow to take over miniscreen
            env.pop("PT_MINISCREEN_SYSTEM")

        first_display = get_first_display()
        if first_display is not None:
            env["DISPLAY"] = first_display

        return env

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()

    def stop(self) -> None:
        if self.process:
            logger.info(f"Stopping project '{self.config.title}'")
            self.process.terminate()
            self.process = None

    def cleanup(self) -> None:
        if self.subscribe_client:
            self.subscribe_client.stop_listening()
            self.subscribe_client = None

    def remove(self) -> None:
        logger.info(
            f"Removing project '{self.config.title}' folder '{self.config.path}'"
        )
        shutil.rmtree(self.config.path)

    def wait(self):
        if not self.process:
            return

        exit_code = self.process.wait()
        logger.info(
            f"Project '{self.config.title}' finished with exit code {exit_code}"
        )

        if self.process and exit_code not in (0, -9):
            raise Exception(f"Project finished with exit code {exit_code}")

    def write_logs(self):
        file = Path(self.config.logfile)
        if file.exists():
            file.unlink()

        with open(self.config.logfile, "a") as f:
            while self.process or not self.log_queue.empty():
                try:
                    line = self.log_queue.get_nowait()
                    f.write(line)
                except Exception:
                    sleep(0.5)

    def run(self):
        logger.info(f"Starting project '{self.config.title}'")
        user = get_user_using_first_display()

        self.process = Popen(
            split(self.config.start),
            stdout=PIPE,
            stderr=PIPE,
            env=self._get_environment(),
            cwd=self.config.path,
            preexec_fn=lambda: switch_user(user),
            text=True,
        )

        def queue_logs(stream):
            for line in iter(stream.readline, ""):
                self.log_queue.put(line)
            stream.close()

        Thread(target=queue_logs, args=[self.process.stdout], daemon=True).start()
        Thread(target=queue_logs, args=[self.process.stderr], daemon=True).start()
        Thread(target=self.write_logs, daemon=True).start()

        self._handle_exit_condition()

    def _handle_exit_condition(self):
        try:
            exit_condition = ProjectExitCondition[self.config.exit_condition.upper()]
        except Exception:
            exit_condition = ProjectExitCondition.FLICK_POWER

        logger.info(f"Using exit condition '{exit_condition.name}'")

        event_callback = {}
        if exit_condition == ProjectExitCondition.FLICK_POWER:
            event_callback = {Message.PUB_V3_BUTTON_POWER_PRESSED: self.stop}
        elif exit_condition == ProjectExitCondition.HOLD_CANCEL:
            CANCEL_BUTTON_PRESS_TIME = 3

            timer = Timer(CANCEL_BUTTON_PRESS_TIME, self.stop)

            def on_cancel_button_pressed():
                nonlocal timer  # noqa: F824
                timer.cancel()
                timer = Timer(CANCEL_BUTTON_PRESS_TIME, self.stop)
                timer.start()

            def on_cancel_button_release():
                nonlocal timer  # noqa: F824
                timer.cancel()

            event_callback = {
                Message.PUB_V3_BUTTON_CANCEL_PRESSED: on_cancel_button_pressed,
                Message.PUB_V3_BUTTON_CANCEL_RELEASED: on_cancel_button_release,
            }

        if exit_condition != ProjectExitCondition.NONE:
            self.subscribe_client = PTDMSubscribeClient()
            self.subscribe_client.initialise(event_callback)
            self.subscribe_client.start_listening()
