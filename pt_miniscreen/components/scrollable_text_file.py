from threading import Thread
from typing import Optional
from pt_miniscreen.components.scrollable import Scrollable
from pt_miniscreen.utils import VIEWPORT_HEIGHT, TextFile, text_to_image
import PIL.Image
import logging


logger = logging.getLogger(__name__)


def concatenate(im1, im2):
    dst = PIL.Image.new("1", (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


class ImageArray:
    def __init__(self):
        self.images = {}
        self.image = text_to_image("")
        self._last_used_index = 0

    def add(self, pos, image):
        if pos not in self.images:
            self.images[pos] = image
            self._update()

    def _update(self):
        last_used = self._last_used_index
        image = self.image

        for i in range(last_used + 1, len(self.images)):
            if i >= len(self.images):
                break
            image = concatenate(image, self.images[i])
            self._last_used_index = i
            self.image = image


class ScrollableTextFile(Scrollable):
    LINES_PER_IMAGE = 30
    file: Optional[TextFile]

    def __init__(self, path, **kwargs) -> None:
        initial_text = "..."
        try:
            self.file = TextFile(path)
            if self.file.len == 0:
                initial_text = "Log file is empty"
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            self.file = None
            initial_text = "Couldn't read log file"

        self.start_line = 0
        self.is_loading = False
        self.image_array = ImageArray()

        super().__init__(
            image=text_to_image(initial_text),
            initial_state={"last_line_loaded": 0},
            **kwargs,
        )

        if self.file and self.file.len > 0:
            self._load_images(start_line=0, lines=self.LINES_PER_IMAGE)
            self.state.update({"image": self.image_array.image})

    def _load_images(self, start_line, lines):
        if self.file is None or self.is_loading:
            return

        self.is_loading = True
        if start_line + lines > self.file.len:
            lines = self.file.len - start_line + 1

        if lines == 0:
            return

        logger.info(
            f"Loading images from lines {start_line} to {start_line + lines - 1}"
        )
        for i in range(start_line, start_line + lines):
            self.image_array.add(
                i, text_to_image(text=self.file.line(i), wrap_margin=self.GUTTER_WIDTH)
            )
            self.state.update({"last_line_loaded": start_line + lines})

        self.is_loading = False

    def update_state(self):
        if self.file is None or self.file.len == 0:
            return

        super().update_state()

        if self.state["speed"] == 0:
            return

        # Load more lines when getting to the bottom of the image
        last_line_loaded = self.state["last_line_loaded"]
        if (
            self.state["speed"] > 0
            and self.state["y_pos"] > self.state["image"].height - VIEWPORT_HEIGHT * 3
            and last_line_loaded <= self.file.len
        ):
            Thread(
                target=self._load_images,
                args=(last_line_loaded, self.LINES_PER_IMAGE),
                daemon=True,
            ).start()

        self.state.update({"image": self.image_array.image})
