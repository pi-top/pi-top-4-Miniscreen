import atexit
import configparser
import logging
import os
from enum import Enum, auto
from functools import partial
from pathlib import Path
from shlex import split
from subprocess import Popen, PIPE
from time import sleep
from threading import Timer, Thread
from typing import Callable, List, Optional, Type, Union

from pitop.common.current_session_info import (
    get_first_display,
    get_user_using_first_display,
)
from pitop.common.switch_user import switch_user
from pitop.common.ptdm import Message, PTDMSubscribeClient

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


PACKAGE_DIRECTORY = os.path.abspath(f"{__file__}/../../..")


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


class ProjectExitCondition(Enum):
    FLICK_POWER = auto()
    HOLD_CANCEL = auto()
    NONE = auto()


class Project:
    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        self.subscribe_client = None
        self.process = None
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
            self.process.kill()
            self.process = None

    def cleanup(self) -> None:
        if self.subscribe_client:
            self.subscribe_client.stop_listening()
            self.subscribe_client = None

    def wait(self):
        if not self.process:
            return

        exit_code = self.process.wait()
        logger.info(
            f"Project '{self.config.title}' finished with exit code {exit_code}"
        )
        if exit_code != 0 and self.process.stderr:
            raise Exception(self.process.stderr.read().decode())

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
        )
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


class ProjectState(Enum):
    IDLE = auto()
    STARTING = auto()
    RUNNING = auto()
    PROJECT_USES_MINISCREEN = auto()
    STOPPING = auto()
    ERROR = auto()


class ProjectPage(Component):
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

    def on_state_change(self, previous_state):
        if self.state["project_state"] != previous_state["project_state"]:
            self.text.state.update({"text": self.displayed_text})

    def set_user_controls_miniscreen(self, user_using_miniscreen):
        if user_using_miniscreen:
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


class ProjectRow(Component):
    def __init__(self, project_config: ProjectConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = self.create_child(
            MarqueeText,
            text=project_config.title,
            font_size=10,
            align="center",
            vertical_align="center",
        )
        self.page = partial(
            ProjectPage,
            project_config,
        )

    def render(self, image):
        return self.text.render(image)


class EmptyProjectRow(Component):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.page = None
        self.text = self.create_child(
            MarqueeText,
            text="No projects found",
            font_size=10,
            align="center",
            vertical_align="center",
        )

    def render(self, image):
        return self.text.render(image)


class ProjectDirectoryRow(Component):
    def __init__(self, title: str, projects_directory: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = self.create_child(
            MarqueeText,
            text=title,
            font_size=10,
            align="center",
            vertical_align="center",
        )
        self.page = partial(
            ProjectList,
            projects_directory,
        )

    def render(self, image):
        return self.text.render(image)


class ProjectDirectoryList(SelectableList):
    PROJECT_DIRECTORY_LOOKUP = {
        "My Projects": "/home/pi/Desktop/Projects/",
        "Further": "/home/pi/further/",
        "pi-top [4] Demos": f"{PACKAGE_DIRECTORY}/demo_projects/pi_top_4/",
        "Electronics Kit": f"{PACKAGE_DIRECTORY}/demo_projects/electronics/",
        "Robotics Kit": f"{PACKAGE_DIRECTORY}/demo_projects/robotics/",
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(
            Rows=self.load_directory_rows(),
            num_visible_rows=5,
            **kwargs,
        )

    def directory_has_projects(self, directory):
        for file in Path(directory).glob("*/*.cfg"):
            try:
                ProjectConfig.from_file(file)
                return True
            except InvalidConfigFile:
                pass
        return False

    def load_directory_rows(self) -> List:
        rows: List[Union[Type[EmptyProjectRow], partial[ProjectDirectoryRow]]] = []
        for title, root_dir in self.PROJECT_DIRECTORY_LOOKUP.items():
            if self.directory_has_projects(root_dir):
                rows.append(
                    partial(
                        ProjectDirectoryRow, projects_directory=root_dir, title=title
                    )
                )

        if len(rows) == 0:
            rows.append(EmptyProjectRow)

        return rows


class ProjectList(SelectableList):
    def __init__(self, directory, **kwargs) -> None:
        self.directory = directory
        super().__init__(
            Rows=self.load_project_rows(),
            num_visible_rows=5,
            **kwargs,
        )

    def load_project_rows(self) -> List:
        rows: List[Union[Type[EmptyProjectRow], partial[ProjectRow]]] = []

        files = Path(self.directory).glob("*/*.cfg")

        # Sort found files by date/time of last modification
        for file in sorted(files, key=os.path.getmtime, reverse=True):
            try:
                logger.info(f"Trying to read {file}")
                project_config = ProjectConfig.from_file(file)
                logger.info(f"Found project {project_config.title}")
                rows.append(partial(ProjectRow, project_config))
            except InvalidConfigFile as e:
                logger.error(f"Error parsing {file}: {e}")

        if len(rows) == 0:
            rows.append(EmptyProjectRow)

        return rows


class ProjectsMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="Projects",
            image_path=get_image_file_path("menu/projects.gif"),
            Pages=[ProjectDirectoryList],
        )
