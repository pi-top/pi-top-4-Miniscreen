from collections.abc import Callable
import logging
import os
from functools import partial
from pathlib import Path
from typing import List, Type, Union

from pt_miniscreen.components.enterable_selectable_list import (
    EnterableSelectableList,
)
from pt_miniscreen.components.confirmation_page import ConfirmationPage
from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.components.mixins import Enterable
from pt_miniscreen.components.scrollable_text_file import ScrollableTextFile
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.pages.root.project_base import (
    DefaultProjectInfoList,
    InvalidConfigFile,
    PACKAGE_DIRECTORY,
    Project,
    ProjectConfig,
    ProjectFolderInfo,
    ProjectPage,
)
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


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


def directory_contains_projects(directory: str, recurse: bool = False) -> bool:
    search_pattern = "**/*.cfg" if recurse else "*/*.cfg"
    for file in Path(directory).glob(search_pattern):
        try:
            ProjectConfig.from_file(file)
            return True
        except InvalidConfigFile:
            pass
    return False


def get_folders_with_projects(folders: List[ProjectFolderInfo]) -> List:
    rows: List[Union[Type[EmptyProjectRow], partial[Row]]] = []

    for project_dir in folders:
        if not directory_contains_projects(
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


class ProjectOverviewList(EnterableSelectableList):
    def __init__(self, directory, **kwargs) -> None:
        self.directory = directory
        super().__init__(Rows=self.load_rows(**kwargs), **kwargs)

    def load_rows(self, **kwargs) -> List:
        def on_delete():
            rows = self.load_rows()
            start_index = 0
            self.rows = [
                self.create_child(Row)
                for Row in rows[
                    start_index : start_index + self.state["num_visible_rows"]
                ]
            ]
            self.state.update({"Rows": rows, "top_row_index": start_index})

        rows: List[Union[Type[EmptyProjectRow], partial[Row]]] = []

        files = Path(self.directory).glob("*/*.cfg")

        # Sort found files by date/time of last modification
        for file in sorted(files, key=os.path.getmtime, reverse=True):
            try:
                logger.info(f"Trying to read {file}")
                project_config = ProjectConfig.from_file(file)
                logger.info(f"Found project {project_config.title}")

                rows.append(
                    partial(
                        Row,
                        title=project_config.title,
                        enterable_component=partial(
                            OverviewProjectPage,
                            project_config=project_config,
                            on_delete=on_delete,
                        ),
                    )
                )
            except InvalidConfigFile as e:
                logger.error(f"Error parsing {file}: {e}")

        if len(rows) == 0:
            rows.append(EmptyProjectRow)

        return rows


class LogsPage(ScrollableTextFile):
    def __init__(self, project_config, **kwargs) -> None:
        super().__init__(path=project_config.logfile, **kwargs)


class OverviewProjectPage(EnterableSelectableList):
    animate_enterable_operation = False

    def __init__(
        self, project_config: ProjectConfig, on_delete: Callable, **kwargs
    ) -> None:
        rows: List[partial] = [
            partial(
                Row,
                title="Run",
                enterable_component=partial(ProjectPage, project_config),
            ),
            partial(
                Row,
                title="View Logs",
                enterable_component=partial(LogsPage, project_config),
            ),
        ]

        if PACKAGE_DIRECTORY not in project_config.path:

            def remove_project():
                Project(project_config).remove()
                if callable(on_delete):
                    on_delete()

            rows.append(
                partial(
                    Row,
                    title="Delete",
                    enterable_component=partial(
                        ConfirmationPage,
                        title="Really delete?",
                        confirm_text="Yes",
                        cancel_text="No",
                        on_confirm=remove_project,
                        on_cancel=None,
                    ),
                )
            )

        super().__init__(
            Rows=rows,
            num_visible_rows=3,
            **kwargs,
        )

    def bottom_gutter_icon(self):
        if isinstance(self.selected_row, Row) and self.selected_row.text.text == "Run":
            return get_image_file_path("gutter/play.png")
        return super().bottom_gutter_icon()


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
            Rows=get_folders_with_projects(DefaultProjectInfoList),
        )
