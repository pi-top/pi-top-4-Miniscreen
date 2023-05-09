import os
import logging
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import List, Type, Union

from pt_miniscreen.components.enterable_selectable_list import (
    EnterableSelectableList,
)
from pt_miniscreen.components.confirmation_page import ConfirmationPage
from pt_miniscreen.components.scrollable_text_file import ScrollableTextFile
from pt_miniscreen.pages.root.projects.project import Project
from pt_miniscreen.pages.root.projects.config import ProjectConfig
from pt_miniscreen.pages.root.projects.project_page import ProjectPage
from pt_miniscreen.pages.root.projects.utils import (
    PACKAGE_DIRECTORY,
    EmptyProjectRow,
    Row,
)
from pt_miniscreen.utils import get_image_file_path


from pt_miniscreen.pages.root.projects.utils import InvalidConfigFile

logger = logging.getLogger(__name__)


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
                        # Go back 2 levels to project list
                        on_confirm_pop_elements=2,
                        # Go back to overview page
                        on_cancel_pop_elements=1,
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


class ProjectOverviewList(EnterableSelectableList):
    def __init__(self, directory, **kwargs) -> None:
        self.directory = directory
        super().__init__(Rows=self.load_rows(), **kwargs)

    def load_rows(self) -> List:
        def on_delete():
            self.update_rows(rows=self.load_rows())

        rows: List[Union[Type[EmptyProjectRow], partial[Row]]] = []

        files = Path(self.directory).glob("*/project.cfg")

        # Sort found files by date/time of last modification
        for file in sorted(files, key=os.path.getmtime, reverse=True):
            try:
                logger.debug(f"Trying to read {file}")
                project_config = ProjectConfig.from_file(file)
                logger.debug(f"Found project {project_config.title}")

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
