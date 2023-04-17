import configparser
import logging
from pathlib import Path
from pt_miniscreen.utils import get_image_file_path
from pt_miniscreen.pages.root.projects.enums import ProjectExitCondition
from pt_miniscreen.pages.root.projects.utils import InvalidConfigFile

logger = logging.getLogger(__name__)


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
        self.logfile = f"{self.path}/log.txt"
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

            exit_condition = project_config.get("exit_condition")
            if exit_condition not in ProjectExitCondition.__members__:
                logger.debug(
                    f"Invalid exit condition '{exit_condition}', using FLICK_POWER."
                )
                exit_condition = ProjectExitCondition.FLICK_POWER.name

            return ProjectConfig(
                file=file,
                title=project_config["title"],
                image=project_config.get("image", ""),
                start=project_config["start"],
                exit_condition=exit_condition,
            )
        except Exception as e:
            logger.warning(f"Error parsing file '{file}': {e}")
            raise InvalidConfigFile(e)
