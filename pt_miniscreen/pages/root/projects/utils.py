from pathlib import Path
from dataclasses import dataclass
import logging
import os

from pitop.common.current_session_info import (
    get_user_using_first_display,
)
from pitop.common.switch_user import get_home_directory

from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.components.mixins import Enterable
from pt_miniscreen.core.component import Component


logger = logging.getLogger(__name__)


USER_HOME = get_home_directory(user=get_user_using_first_display())
PACKAGE_DIRECTORY = os.path.abspath(f"{__file__}/../../../..")


class InvalidConfigFile(Exception):
    pass


def directory_contains_projects(directory: str, recurse: bool = False) -> bool:
    from pt_miniscreen.pages.root.projects.config import ProjectConfig

    search_pattern = "**/*.cfg" if recurse else "*/*.cfg"
    for file in Path(directory).glob(search_pattern):
        try:
            ProjectConfig.from_file(file)
            return True
        except InvalidConfigFile:
            pass
    return False


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


class Row(Component, Enterable):
    def __init__(self, title, enterable_component, **kwargs) -> None:
        super().__init__(**kwargs)
        self._component = enterable_component
        self.text = self.create_child(
            MarqueeText,
            text=title,
            font_size=10,
            align="center",
            vertical_align="center",
        )

    @property
    def enterable_component(self):
        return self._component

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
