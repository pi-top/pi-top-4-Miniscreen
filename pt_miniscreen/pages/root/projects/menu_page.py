import logging
import os
from functools import partial
from typing import List, Type, Union

from pt_miniscreen.components.enterable_selectable_list import (
    EnterableSelectableList,
)
from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.pages.root.projects.utils import directory_contains_projects
from pt_miniscreen.pages.root.projects.overview import ProjectOverviewList
from pt_miniscreen.pages.root.projects.utils import (
    ProjectFolderInfo,
    MyProjectsDirectory,
    FurtherDirectory,
    PiTop4DemosDirectory,
    ElectronicsKitDirectory,
    RoboticsKitDirectory,
    Row,
    EmptyProjectRow,
)
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


def get_folders_with_projects(folders: List[ProjectFolderInfo]) -> List:
    rows: List[Union[Type[EmptyProjectRow], partial[Row]]] = []

    for project_dir in folders:
        if not os.path.isdir(project_dir.folder) or not directory_contains_projects(
            project_dir.folder, recurse=project_dir.recurse_search
        ):
            continue

        if project_dir.recurse_search:
            project_folders = []
            for folder in os.listdir(project_dir.folder):
                project_folders.append(
                    ProjectFolderInfo.from_directory(
                        os.path.join(project_dir.folder, folder), title=folder
                    )
                )

            rows.append(
                partial(
                    Row,
                    title=project_dir.title,
                    enterable_component=partial(
                        partial(
                            EnterableSelectableList,
                            Rows=get_folders_with_projects(project_folders),
                        )
                    ),
                )
            )

        else:
            rows.append(
                partial(
                    Row,
                    title=project_dir.title,
                    enterable_component=partial(
                        ProjectOverviewList,
                        directory=project_dir.folder,
                    ),
                )
            )

    if len(rows) == 0:
        rows.append(EmptyProjectRow)

    return rows


class ProjectsMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="Projects",
            image_path=get_image_file_path("menu/projects.gif"),
            Pages=[],
        )

    @property
    def enterable_component(self):
        return partial(
            EnterableSelectableList,
            Rows=get_folders_with_projects(
                [
                    MyProjectsDirectory,
                    FurtherDirectory,
                    PiTop4DemosDirectory,
                    ElectronicsKitDirectory,
                    RoboticsKitDirectory,
                ]
            ),
        )
