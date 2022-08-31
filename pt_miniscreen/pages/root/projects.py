import configparser
import logging
import os
from functools import partial
from pathlib import Path
from shlex import split
from subprocess import Popen
from time import sleep
from typing import List, Type, Union

from pitop.common.current_session_info import get_first_display

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


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
            image = get_image_file_path("menu/settings.gif")
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

    # Print output of commands in english
    env["LANG"] = "en_US.UTF-8"

    return env


def run_project(cmd: str, cwd: str = None):
    logger.info(f"run_project(command_str='{cmd}', cwd='{cwd}')")

    return Popen(
        split(cmd),
        env=get_project_environment(),
        cwd=cwd,
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

    def render(self, image):
        return self.text.render(image)

    def start(self):
        logger.info(
            f"Starting project '{self.project_config.title}': '{self.project_config.start}'"
        )
        sleep(2)
        self.process = run_project(
            self.project_config.start, cwd=self.project_config.path
        )

    def wait(self):
        if self.process is None:
            raise Exception("Nothing to wait ...")
        exit_code = self.process.wait()
        self.process = None
        logger.info(
            f"Project '{self.project_config.title}' finished with exit code {exit_code}"
        )


class ProjectRow(Component):
    def __init__(self, project_config: ProjectConfig, **kwargs) -> None:
        project_config = project_config

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


class ProjectList(SelectableList):
    PROJECT_DIRECTORIES = [
        "/home/pi/Desktop/Projects/",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            Rows=self.load_project_rows(),
            num_visible_rows=5,
            **kwargs,
        )

    def load_project_rows(self) -> List:
        rows: List[Union[Type[EmptyProjectRow], partial[ProjectRow]]] = []
        for root_dir in self.PROJECT_DIRECTORIES:
            files = Path(root_dir).glob("*/*.cfg")
            # Sort found files by date/time of last modification
            for file in sorted(files, key=os.path.getmtime, reverse=True):
                try:
                    logger.info(f"Trying to read {root_dir}/{file}")
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
            image_path=get_image_file_path("menu/network.gif"),
            Pages=[ProjectList],
        )
