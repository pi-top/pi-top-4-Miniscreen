import configparser
import logging
import os
from functools import partial
from pathlib import Path
from shlex import split
from subprocess import Popen
from threading import Thread
from time import sleep
from typing import Callable, List, Type, Union

from pitop.common.current_session_info import (
    get_first_display,
    get_user_using_first_display,
)
from pitop.common.switch_user import switch_user

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.core.components.selectable_list import SelectableList
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
                exit_condition=project_config.get("exit_condition"),
            )
        except Exception as e:
            logger.warning(f"Error parsing file '{file}': {e}")
            raise InvalidConfigFile(e)


def get_project_environment():
    env = os.environ.copy()

    if "PT_MINISCREEN_SYSTEM" in env:
        # Allow to take over miniscreen
        env.pop("PT_MINISCREEN_SYSTEM")

    first_display = get_first_display()
    if first_display is not None:
        env["DISPLAY"] = first_display

    return env


def run_project(cmd: str, cwd: str = None):
    logger.info(f"run_project(command_str='{cmd}', cwd='{cwd}')")
    user = get_user_using_first_display()
    env = get_project_environment()

    return Popen(
        split(cmd),
        env=env,
        cwd=cwd,
        preexec_fn=lambda: switch_user(user),
    )


class ProjectPage(Component):
    def __init__(self, project_config: ProjectConfig, **kwargs):
        self.project_config = project_config
        super().__init__(**kwargs)

        self.process = None
        self.text = self.create_child(
            MarqueeText,
            text=f"Running '{self.project_config.title}'",
            font_size=14,
            align="center",
            vertical_align="center",
        )

    def run(self, on_stop: Callable = None):
        self.start()

        def wait_and_run_on_stop():
            self.wait()
            on_stop()

        if callable(on_stop):
            Thread(target=wait_and_run_on_stop, daemon=True).run()

    def render(self, image):
        return self.text.render(image)

    def start(self):
        logger.info(
            f"Starting project '{self.project_config.title}': '{self.project_config.start}'"
        )
        sleep(3)
        try:
            self.process = run_project(
                self.project_config.start, cwd=self.project_config.path
            )
        except Exception as e:
            logger.error(f"Error starting project: {e}")

    def wait(self):
        if self.process:
            exit_code = self.process.wait()
            logger.info(
                f"Project '{self.project_config.title}' finished with exit code {exit_code}"
            )
            self.process = None


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
