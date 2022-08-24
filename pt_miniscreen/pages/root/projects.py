import configparser
import logging
from functools import partial
from pathlib import Path
from typing import List

from pt_miniscreen.components.menu_page import MenuPage
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components import Image
from pt_miniscreen.core.components.marquee_text import MarqueeText
from pt_miniscreen.core.components.selectable_list import SelectableList
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.utils import get_image_file_path

logger = logging.getLogger(__name__)


class InvalidConfigFile(Exception):
    pass


class ProjectConfig:
    CONFIG_FILE_SECTION = "project"

    def __init__(self, title, image, start, exit_condition, **kwargs) -> None:
        self.title = title
        self.image = image
        self.start = start
        self.exit_condition = exit_condition

    @classmethod
    def from_file(cls, file):
        config = configparser.ConfigParser()
        try:
            config.read(file)
            project_config = config[cls.CONFIG_FILE_SECTION]

            image = project_config.get("image")
            if image is None or not Path(image).is_file():
                image = get_image_file_path("menu/settings.gif")

            return ProjectConfig(
                title=project_config["title"],
                image=image,
                start=project_config["start"],
                exit_condition=project_config["exit_condition"],
            )
        except Exception as e:
            logger.warning(f"Error parsing file '{file}': {e}")
            raise InvalidConfigFile(e)


class ProjectPage(Component):
    def __init__(self, project_config: ProjectConfig, **kwargs):
        self.project_config = project_config
        super().__init__(**kwargs)
        self.text = self.create_child(
            MarqueeText,
            text=self.project_config.title,
            font_size=14,
            align="center",
            vertical_align="center",
        )
        self.image = self.create_child(
            Image,
            image_path=self.project_config.image,
        )

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.text.render,
                    size=(120, 25),
                    pos=(28, 0),
                ),
                layer(
                    self.image.render,
                    size=(25, 25),
                    pos=(0, 0),
                ),
            ],
        )


class ProjectRow(Component):
    def __init__(self, project_config: ProjectConfig, **kwargs) -> None:
        self.project_config = project_config
        super().__init__(**kwargs)
        self.text = self.create_child(
            MarqueeText,
            text=self.project_config.title,
            font_size=10,
            align="center",
            vertical_align="center",
        )
        self.page = partial(ProjectPage, self.project_config)

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.text.render,
                    size=(128, 10),
                    pos=(0, 0),
                ),
            ],
        )


class ProjectList(SelectableList):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            Rows=self.load_project_rows(["/home/pi/Desktop/Projects/"]),
            num_visible_rows=5,
            **kwargs,
        )

    def load_project_rows(self, directories: List) -> List:
        pages = []
        for root_dir in directories:
            for file in Path(root_dir).glob("*/*.cfg"):
                try:
                    logger.info(f"Trying to read {root_dir}/{file}")
                    project_config = ProjectConfig.from_file(file)
                    logger.info(f"Found project {project_config.title}")
                    pages.append(partial(ProjectRow, project_config))
                except InvalidConfigFile as e:
                    logger.error(f"Error parsing {file}: {e}")
        return pages


class ProjectsMenuPage(MenuPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            text="Projects",
            image_path=get_image_file_path("menu/network.gif"),
            Pages=[ProjectList],
        )
