import logging
from threading import Event, Thread
from time import sleep

from PIL.Image import open as open_image, BICUBIC

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
        resize=False,
        resize_resampling=None,
        initial_state={},
        **kwargs,
    ):
        self._image = open_image(image_path) if image_path else None
        self.stop_animating_event = Event()

        super().__init__(
            **kwargs,
            initial_state={
                "image_path": image_path,
                "frame": 0,
                "loop": loop,
                "align": align,
                "vertical_align": vertical_align,
                "resize": resize,
                "resize_resampling": (
                    resize_resampling if resize_resampling else BICUBIC
                ),
                **initial_state,
            },
        )

        if self._image and self._image.is_animated:
            self._start_animating()

    @property
    def image(self):
        if not self._image:
            return None

        if self.state["resize"] and self.size:
            return self._image.resize(self.size, self.state["resize_resampling"])

        return self._image.copy()

    @image.setter
    def image(self, _):
        raise Exception(
            "Setting image property directly not allowed, update image_path in state"
        )

    def cleanup(self):
        self.stop_animating_event.set()

    def _start_animating(self):
        # stop previous animation if it exists
        self.stop_animating_event.set()

        # create stop event for new thread
        self.stop_animating_event = Event()
        Thread(
            target=self._animate, args=[self.stop_animating_event], daemon=True
        ).start()

    def _animate(self, stop_event):
        if not self._image.is_animated:
            logger.debug("image is not animated, unable to start animating")
            return

        while True:
            sleep(self._image.info["duration"] / 1000)

            self.active_event.wait()

            if stop_event.is_set():
                return

            next_frame = self.state["frame"] + 1
            if self.state["loop"] and next_frame >= self._image.n_frames:
                next_frame = 0

            try:
                self._image.seek(next_frame)
                self.state.update({"frame": next_frame})
            except EOFError:
                # bail if image has no more frames
                stop_event.set()
                return

    def on_state_change(self, previous_state):
        # on loop change
        loop = self.state["loop"]
        if self.state["loop"] != previous_state["loop"]:
            if loop and self._image.is_animated:
                self._start_animating()

            if not loop and self.stop_animating_event:
                self.stop_animating_event.set()

        # on image_path change
        image_path = self.state["image_path"]
        if image_path != previous_state["image_path"]:
            if self.stop_animating_event:
                self.stop_animating_event.set()

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

        image.paste(self.image, self._get_pos(image.size))
        return image
