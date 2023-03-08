import atexit
import configparser
from dataclasses import dataclass
import logging
import os
from queue import Queue
import shutil
from enum import Enum, auto
from pathlib import Path
from shlex import split
from subprocess import PIPE, Popen
from time import sleep
from threading import Timer, Thread
from typing import Callable, Optional

from pitop.common.current_session_info import (
    get_first_display,
    get_user_using_first_display,
)
from pitop.common.switch_user import get_home_directory, switch_user
from pitop.common.ptdm import Message, PTDMSubscribeClient
from pt_miniscreen.components.mixins import BlocksMiniscreenButtons, Poppable
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.text import Text

from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


USER_HOME = get_home_directory(user=get_user_using_first_display())
PACKAGE_DIRECTORY = os.path.abspath(f"{__file__}/../../..")


class ProjectState(Enum):
    IDLE = auto()
    STARTING = auto()
    RUNNING = auto()
    PROJECT_USES_MINISCREEN = auto()
    STOPPING = auto()
    ERROR = auto()


class ProjectExitCondition(Enum):
    FLICK_POWER = auto()
    HOLD_CANCEL = auto()
    NONE = auto()


class InvalidConfigFile(Exception):
    pass


class ProjectConfig:
    CONFIG_FILE_SECTION = "project"

    def __init__(
        self,
        file: str,
        title: str,
        image: str,
        start: str,
        exit_condition: str,
        **kwargs,
    ) -> None:
        self.file = file
        self.path = Path(file).parent.absolute().as_posix()
        self.logfile = f"{self.path}/log.txt"
        self.title = title
        if len(image) == 0 or not Path(image).is_file():
            image = get_image_file_path("menu/projects.gif")
        self.image = image
        self.start = start
        self.exit_condition = exit_condition

    @classmethod
    def from_file(cls, file):
        config = configparser.ConfigParser()
        try:
            config.read(file)
            project_config = config[cls.CONFIG_FILE_SECTION]

            return ProjectConfig(
                file=file,
                title=project_config["title"],
                image=project_config.get("image", ""),
                start=project_config["start"],
                exit_condition=project_config.get(
                    "exit_condition", ProjectExitCondition.FLICK_POWER.name
                ),
            )
        except Exception as e:
            logger.warning(f"Error parsing file '{file}': {e}")
            raise InvalidConfigFile(e)


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
            exit_condition = ProjectExitCondition.NONE

        logger.info(f"Using exit condition '{exit_condition.name}'")

        if exit_condition == ProjectExitCondition.FLICK_POWER:
            event_callback = {Message.PUB_V3_BUTTON_POWER_PRESSED: self.stop}
        elif exit_condition == ProjectExitCondition.HOLD_CANCEL:
            CANCEL_BUTTON_PRESS_TIME = 3

            timer = Timer(CANCEL_BUTTON_PRESS_TIME, self.stop)

            def on_cancel_button_pressed():
                nonlocal timer
                timer.cancel()
                timer = Timer(CANCEL_BUTTON_PRESS_TIME, self.stop)
                timer.start()

            def on_cancel_button_release():
                nonlocal timer
                timer.cancel()

            event_callback = {
                Message.PUB_V3_BUTTON_CANCEL_PRESSED: on_cancel_button_pressed,
                Message.PUB_V3_BUTTON_CANCEL_RELEASED: on_cancel_button_release,
            }

        if exit_condition != ProjectExitCondition.NONE:
            self.subscribe_client = PTDMSubscribeClient()
            self.subscribe_client.initialise(event_callback)
            self.subscribe_client.start_listening()


class ProjectPage(Component, Poppable, BlocksMiniscreenButtons):
    def __init__(self, project_config: ProjectConfig, **kwargs):
        self.project_config = project_config
        super().__init__(**kwargs, initial_state={"project_state": ProjectState.IDLE})

        self.text = self.create_child(
            Text,
            text=self.displayed_text,
            font_size=10,
            align="center",
            vertical_align="center",
        )

        self.run(on_stop=self.pop)

    @property
    def block_buttons(self):
        return True

    def on_state_change(self, previous_state):
        if self.state["project_state"] != previous_state["project_state"]:
            self.text.state.update({"text": self.displayed_text})

    def set_user_controls_miniscreen(self, user_using_miniscreen):
        if user_using_miniscreen and self.is_running:
            self.state.update({"project_state": ProjectState.PROJECT_USES_MINISCREEN})

    @property
    def displayed_text(self) -> str:
        text = ""
        project_state = self.state.get("project_state")
        if project_state == ProjectState.ERROR:
            text = f"There was an error while running '{self.project_config.title}'..."
        elif project_state == ProjectState.RUNNING:
            text = f"'{self.project_config.title}' is running..."
        elif project_state == ProjectState.STOPPING:
            text = f"Stopping '{self.project_config.title}'..."
        elif project_state == ProjectState.STARTING:
            text = f"Starting '{self.project_config.title}'..."
            try:
                exit_condition = ProjectExitCondition[
                    self.project_config.exit_condition.upper()
                ]
                if exit_condition == ProjectExitCondition.FLICK_POWER:
                    text += "\nFlick the power button to exit"
                elif exit_condition == ProjectExitCondition.HOLD_CANCEL:
                    text += "\nHold 'X' button for 3 seconds to exit"
            except Exception:
                pass

        return text

    def render(self, image):
        return self.text.render(image)

    @property
    def is_running(self):
        return self.state.get("project_state") == ProjectState.RUNNING

    def run(self, on_stop: Optional[Callable] = None):
        logger.info(
            f"Running project '{self.project_config.title}': '{self.project_config.start}'"
        )
        Thread(target=self._run_in_background, args=(on_stop,), daemon=True).start()

    def _run_in_background(self, on_stop: Optional[Callable] = None):
        """Project needs to run & be waited in the background since otherwise
        button events are queued and then passed & processed by the main app
        once the project finishes.

        When running in a thread, events are handled as they arrive and
        skipped since user is in control.
        """
        self.state.update({"project_state": ProjectState.STARTING})
        sleep(3)
        try:
            with Project(self.project_config) as project:
                project.run()
                self.state.update({"project_state": ProjectState.RUNNING})
                project.wait()
                self.state.update({"project_state": ProjectState.STOPPING})
        except Exception as e:
            logger.error(f"Error running project: {e}")
            self.state.update({"project_state": ProjectState.ERROR})
        finally:
            sleep(2)
            if callable(on_stop):
                on_stop()
            self.state.update({"project_state": ProjectState.IDLE})


@dataclass
class ProjectFolderInfo:
    folder: str
    title: str
    exclude_dirs: list
    recurse_search: bool = False

    @classmethod
    def from_directory(cls, directory, title):
        return cls(folder=directory, title=title, exclude_dirs=[], recurse_search=False)


class MyProjectsDirectory(ProjectFolderInfo):
    folder = os.path.join(USER_HOME, "Desktop/Projects")
    exclude_dirs = ["Further"]
    title = "My Projects"


class FurtherDirectory(ProjectFolderInfo):
    folder = os.path.join(USER_HOME, "Desktop/Projects/Further")
    title = "Further"
    recurse_search = True


class PiTop4DemosDirectory(ProjectFolderInfo):
    folder = f"{PACKAGE_DIRECTORY}/demo_projects/pi_top_4/"
    title = "pi-top [4] Demos"


class ElectronicsKitDirectory(ProjectFolderInfo):
    title = "Electronics Kit"
    folder = f"{PACKAGE_DIRECTORY}/demo_projects/electronics/"


class RoboticsKitDirectory(ProjectFolderInfo):
    title = "Robotics Kit"
    folder = f"{PACKAGE_DIRECTORY}/demo_projects/robotics/"


DefaultProjectInfoList = [
    MyProjectsDirectory,
    FurtherDirectory,
    PiTop4DemosDirectory,
    ElectronicsKitDirectory,
    RoboticsKitDirectory,
]
