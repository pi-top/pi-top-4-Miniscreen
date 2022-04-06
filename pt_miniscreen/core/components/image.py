import logging
from threading import Event, Thread
from time import sleep

from PIL.Image import open as open_image

from ..component import Component
from ..utils import offset_to_center

logger = logging.getLogger(__name__)


class Image(Component):
    def __init__(
        self,
        image_path=None,
        loop=True,
        align="left",
        vertical_align="top",
        initial_state={},
        **kwargs,
    ):
        self._image = open_image(image_path) if image_path else None

        super().__init__(
            **kwargs,
            initial_state={
                "image_path": image_path,
                "frame": 0,
                "loop": loop,
                "align": align,
                "vertical_align": vertical_align,
                **initial_state,
            },
        )

        self._stop_animating_event = Event()
        if self.image and self.image.is_animated:
            self._start_animating()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, _):
        raise Exception(
            "Setting image property directly not allowed, update image_path in state"
        )

    def cleanup(self):
        self._stop_animating_event.set()

    def _start_animating(self):
        # stop previous animation if it exists
        self._stop_animating_event.set()

        # create stop event for new thread
        self._stop_animating_event = Event()
        Thread(
            target=self._animate, args=[self._stop_animating_event], daemon=True
        ).start()

    def _animate(self, stop_event):
        if not self.image.is_animated:
            logger.debug("image is not animated, unable to start animating")
            return

        while True:
            sleep(self.image.info["duration"] / 1000)

            if stop_event.is_set():
                return

            next_frame = self.state["frame"] + 1
            if self.state["loop"] and next_frame >= self.image.n_frames:
                next_frame = 0

            try:
                self.image.seek(next_frame)
                self.state.update({"frame": next_frame})
            except EOFError:
                # bail if image has no more frames
                return

    def on_state_change(self, previous_state):
        image_path = self.state["image_path"]

        # do nothing if image_path hasn't changed
        if image_path == previous_state["image_path"]:
            return

        # stop animating gif if image has changed
        if self._stop_animating_event:
            self._stop_animating_event.set()

        # bail if image_path is now None
        if image_path is None:
            self._image = None
            return

        # update self.image
        self._image = open_image(image_path)

        # reset frame state if needed
        if self.state["frame"] != 0:
            self.state.update({"frame": 0})

        # start animating image if it is animated
        if self._image.is_animated:
            self._start_animating()

    def _get_x_pos(self, container_width):
        if self.state["align"] == "center":
            return offset_to_center(container_width, self.image.width)

        if self.state["align"] == "right":
            return container_width - self.image.width

        return 0

    def _get_y_pos(self, container_height):
        if self.state["vertical_align"] == "center":
            return offset_to_center(container_height, self.image.height)

        if self.state["vertical_align"] == "bottom":
            return container_height - self.image.height

        return 0

    def _get_pos(self, container_size):
        return (self._get_x_pos(container_size[0]), self._get_y_pos(container_size[1]))

    def render(self, image):
        if not self._image:
            return image

        image.paste(self._image, self._get_pos(image.size))
        return image
