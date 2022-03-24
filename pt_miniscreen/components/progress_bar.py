import logging
from typing import Callable, Union

import PIL.ImageDraw

from pt_miniscreen.core.component import Component

logger = logging.getLogger(__name__)


class ProgressBar(Component):
    def __init__(
        self,
        progress: Union[Callable, float],
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            initial_state={"progress": progress() if callable(progress) else progress},
        )

        if callable(progress):
            self._get_progress = progress
            self.create_interval(self.update_progress)

    def update_progress(self):
        self.state.update({"progress": self._get_progress()})

    def render(self, image):
        margin = 1
        draw = PIL.ImageDraw.Draw(image)

        try:
            percent = self.state["progress"]
        except Exception as e:
            logger.error(f"progress_bar error: {e}.")
            percent = 0.0

        draw.rectangle(
            (0, 0) + (image.width - margin, image.height - margin), "black", "white"
        )
        draw.rectangle(
            (0, 0) + (image.width * percent / 100.0, image.height - margin),
            "white",
            "white",
        )

        return image
