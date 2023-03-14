import logging
from typing import Optional, Callable
from time import sleep
from threading import Thread

from pt_miniscreen.pages.root.projects.enums import ProjectExitCondition, ProjectState
from pt_miniscreen.pages.root.projects.project import Project

from pt_miniscreen.components.mixins import BlocksMiniscreenButtons, Poppable
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.pages.root.projects.config import ProjectConfig


logger = logging.getLogger(__name__)


class ProjectPage(Component, Poppable, BlocksMiniscreenButtons):
    def __init__(self, project_config: ProjectConfig, **kwargs):
        self.project_config = project_config
        super().__init__(**kwargs, initial_state={"project_state": ProjectState.IDLE})

        self.text = self.create_child(
            Text,
            text=self.displayed_text,
            font_size=10,
            align="center",
            vertical_align="center",
        )

        self.run(on_stop=self.pop)

    @property
    def block_buttons(self):
        return True

    def on_state_change(self, previous_state):
        if self.state["project_state"] != previous_state["project_state"]:
            self.text.state.update({"text": self.displayed_text})

    def set_user_controls_miniscreen(self, user_using_miniscreen):
        if user_using_miniscreen and self.is_running:
            self.state.update({"project_state": ProjectState.PROJECT_USES_MINISCREEN})

    @property
    def displayed_text(self) -> str:
        text = ""
        project_state = self.state.get("project_state")
        if project_state == ProjectState.ERROR:
            text = f"There was an error while running '{self.project_config.title}'..."
        elif project_state == ProjectState.RUNNING:
            text = f"'{self.project_config.title}' is running..."
        elif project_state == ProjectState.STOPPING:
            text = f"Stopping '{self.project_config.title}'..."
        elif project_state == ProjectState.STARTING:
            text = f"Starting '{self.project_config.title}'..."
            try:
                exit_condition = ProjectExitCondition[
                    self.project_config.exit_condition.upper()
                ]
                if exit_condition == ProjectExitCondition.FLICK_POWER:
                    text += "\nFlick the power button to exit"
                elif exit_condition == ProjectExitCondition.HOLD_CANCEL:
                    text += "\nHold 'X' button for 3 seconds to exit"
            except Exception as e:
                logger.warning(f"Couldn't set exit condition text: {e}")

        return text

    def render(self, image):
        return self.text.render(image)

    @property
    def is_running(self):
        return self.state.get("project_state") == ProjectState.RUNNING

    def run(self, on_stop: Optional[Callable] = None):
        logger.info(
            f"Running project '{self.project_config.title}': '{self.project_config.start}'"
        )
        Thread(target=self._run_in_background, args=(on_stop,), daemon=True).start()

    def _run_in_background(self, on_stop: Optional[Callable] = None):
        """Project needs to run & be waited in the background since otherwise
        button events are queued and then passed & processed by the main app
        once the project finishes.

        When running in a thread, events are handled as they arrive and
        skipped since user is in control.
        """
        self.state.update({"project_state": ProjectState.STARTING})
        sleep(3)
        try:
            with Project(self.project_config) as project:
                project.run()
                self.state.update({"project_state": ProjectState.RUNNING})
                project.wait()
                self.state.update({"project_state": ProjectState.STOPPING})
        except Exception as e:
            logger.error(f"Error running project: {e}")
            self.state.update({"project_state": ProjectState.ERROR})
        finally:
            sleep(2)
            if callable(on_stop):
                on_stop()
            self.state.update({"project_state": ProjectState.IDLE})
