import logging
from functools import partial

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.pages.root.projects.overview import FolderOverviewList
from pt_miniscreen.pages.root.projects.utils import (
    MyProjectsDirectory,
    FurtherDirectory,
    PiTop4DemosDirectory,
    ElectronicsKitDirectory,
    RoboticsKitDirectory,
)
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


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
            FolderOverviewList,
            folder_info=[
                MyProjectsDirectory,
                FurtherDirectory,
                PiTop4DemosDirectory,
                ElectronicsKitDirectory,
                RoboticsKitDirectory,
            ],
        )
