import os
import logging
from functools import partial
from shutil import rmtree
from typing import List, Union
from pathlib import Path
from weakref import ref

from pt_miniscreen.components.mixins import UpdatableByChild
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
    InvalidConfigFile,
    Row,
    ProjectFolderInfo,
    directory_contains_projects,
)
from pt_miniscreen.utils import get_image_file_path, isclass


logger = logging.getLogger(__name__)


class LogsPage(ScrollableTextFile):
    def __init__(self, project_config, **kwargs) -> None:
        super().__init__(path=project_config.logfile, **kwargs)


class OverviewProjectPage(EnterableSelectableList):
    animate_enterable_operation = False

    def __init__(
        self,
        project_config: ProjectConfig,
        parent: UpdatableByChild,
        **kwargs,
    ) -> None:
        self.parent_ref = ref(parent)

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

            rows.append(
                partial(
                    Row,
                    title="Delete",
                    enterable_component=partial(
                        ConfirmationPage,
                        parent=parent,
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


class SupportsDeleteAll:
    def get_rows(self) -> List:
        raise NotImplementedError

    def can_be_deleted(self) -> bool:
        raise NotImplementedError

    def add_delete_row(
        self, rows: List, folder_info: Union[List[ProjectFolderInfo], ProjectFolderInfo]
    ) -> None:
        if len(rows) == 0 or isclass(rows[0], EmptyProjectRow):
            return

        if not isinstance(folder_info, list):
            # Convert to array to support all scenarios
            folder_info = [folder_info]

        def delete_all():
            for x in folder_info:
                rmtree(x.folder, ignore_errors=True)

        if all([folder.can_remove_all for folder in folder_info]):
            rows.insert(
                0,
                partial(
                    Row,
                    title="Delete All",
                    enterable_component=partial(
                        ConfirmationPage,
                        parent=self,
                        title="Really delete?",
                        confirm_text="Yes",
                        cancel_text="No",
                        on_confirm=delete_all,
                        on_cancel=None,
                        # Go back 2 levels to projects/users list
                        on_confirm_pop_elements=2,
                        # Go back to overview page
                        on_cancel_pop_elements=1,
                    ),
                ),
            )


class FolderOverviewList(EnterableSelectableList, SupportsDeleteAll, UpdatableByChild):
    def __init__(
        self,
        folder_info: Union[List[ProjectFolderInfo], ProjectFolderInfo],
        parent: UpdatableByChild,
        **kwargs,
    ) -> None:
        self.folder_info = folder_info
        self.parent_ref = ref(parent)

        # Get an array of ProjectFolderInfo objects of interest
        self.folders: List[ProjectFolderInfo]
        if isinstance(self.folder_info, ProjectFolderInfo):
            self.folders = get_nested_directories(self.folder_info)
        elif not isinstance(self.folder_info, list):
            self.folders = [self.folder_info]
        else:
            self.folders = self.folder_info

        super().__init__(Rows=self.get_rows(), **kwargs)
        self._set_selected_row()

    def _set_selected_row(self) -> None:
        if self.can_be_deleted():
            # Don't select the 'Delete All' row
            self.select_next_row(animate_scroll=False)

    def can_be_deleted(self) -> bool:
        return (
            len(self.state["Rows"]) > 0
            and not isinstance(self.state["Rows"][0], EmptyProjectRow)
            and all([folder_info.can_remove_all for folder_info in self.folders])
        )

    def on_child_action(self) -> None:
        # Update component & parent rows to reflect changes
        self.update_rows(rows=self.get_rows())
        self._set_selected_row()

        parent_ref = self.parent_ref()
        if parent_ref and isinstance(parent_ref, UpdatableByChild):
            parent_ref.on_child_action()

    def get_rows(self) -> List:
        rows = rows_for_folders(folders=self.folders, parent=self)
        self.add_delete_row(rows, self.folders)
        return rows


class ProjectOverviewList(EnterableSelectableList, SupportsDeleteAll, UpdatableByChild):
    def __init__(
        self,
        folder_info: ProjectFolderInfo,
        parent: UpdatableByChild,
        **kwargs,
    ) -> None:
        self.folder_info = folder_info
        self.parent_ref = ref(parent)
        super().__init__(Rows=self.get_rows(), **kwargs)
        self._set_selected_row()

    def _set_selected_row(self) -> None:
        if self.can_be_deleted():
            # Don't select the 'Delete All' row
            self.select_next_row(animate_scroll=False)

    def on_child_action(self) -> None:
        # Update component & parent rows to reflect changes
        self.update_rows(rows=self.get_rows())
        self._set_selected_row()

        parent_ref = self.parent_ref()
        if parent_ref and isinstance(parent_ref, UpdatableByChild):
            parent_ref.on_child_action()

    def get_rows(self) -> List:
        rows = get_project_rows(self.folder_info, self)
        self.add_delete_row(rows, self.folder_info)
        return rows

    def can_be_deleted(self) -> bool:
        return (
            len(self.state["Rows"]) > 0
            and not isinstance(self.state["Rows"][0], EmptyProjectRow)
            and self.folder_info.can_remove_all
        )


def get_nested_directories(
    folder_info: ProjectFolderInfo,
) -> List[ProjectFolderInfo]:
    """Returns an array of 'ProjectFolderInfo' objects representing the
    directories inside 'folder_info'."""
    folders = []
    for folder in os.listdir(folder_info.folder):
        folders.append(
            ProjectFolderInfo.from_directory(
                directory=os.path.join(folder_info.folder, folder), title=folder
            )
        )
    return folders


def rows_for_folders(
    folders: List[ProjectFolderInfo],
    parent: UpdatableByChild,
) -> List[Union[partial[EmptyProjectRow], partial[Row]]]:
    """Returns a List with Rows representing the directories with projects
    found in the given 'folders' array.

    The returned list can contain 'ProjectOverviewList' objects if
    projects were found inside a folder and 'FolderOverviewList' objects
    if projects were found in deeper levels of a folder.
    """
    rows: List[Union[partial[EmptyProjectRow], partial[Row]]] = []

    for project_dir in folders:
        if not os.path.isdir(project_dir.folder) or not directory_contains_projects(
            project_dir.folder, recurse=project_dir.recurse_search
        ):
            # No projects available in this folder
            continue

        if project_dir.recurse_search:
            folders = get_nested_directories(project_dir)
            if len(folders) > 0:
                rows.append(
                    partial(
                        Row,
                        title=project_dir.title,
                        enterable_component=partial(
                            FolderOverviewList,
                            folder_info=folders,
                            parent=parent,
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
                        folder_info=project_dir,
                        parent=parent,
                    ),
                )
            )

    if len(rows) == 0:
        rows.append(partial(EmptyProjectRow))

    return rows


def get_project_rows(folder_info: ProjectFolderInfo, parent: UpdatableByChild) -> List:
    """Returns a List with Rows representing the projects found in the provided
    'folder_info'."""
    rows: List[Union[partial[EmptyProjectRow], partial[Row]]] = []

    files = Path(folder_info.folder).glob("*/project.cfg")

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
                        parent=parent,
                    ),
                )
            )
        except InvalidConfigFile as e:
            logger.error(f"Error parsing {file}: {e}")

    if len(rows) == 0:
        rows.append(partial(EmptyProjectRow))

    return rows
