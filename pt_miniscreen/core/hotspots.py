import logging
import threading
from math import ceil

from PIL import ImageDraw

from .hotspot import Hotspot
from .utils import apply_layers, layer, rectangle, transition

logger = logging.getLogger(__name__)


class NavigationControllerHotspot(Hotspot):
    transition_duration = 0.25
    smoothness = 1
    width = 0
    default_state = {
        "x_position": 0,
        "stack": [],
        "active_transition": None,
    }

    def __init__(self, initial_stack=[], **kwargs):
        assert len(initial_stack) > 0
        super().__init__(**kwargs)
        self.state["stack"] = [
            self.create_hotspot(Hotspot) for Hotspot in initial_stack
        ]

    @property
    def active_hotspot(self):
        # when popping the top hotspot is being removed and isn't active
        if self.state["active_transition"] == "POP":
            return self.state["stack"][-2]

        return self.state["stack"][-1]

    @property
    def active_index(self):
        return self.state["stack"].index(self.active_hotspot)

    def _transition(self, on_step):
        for step in transition(
            distance=self.width,
            duration=self.transition_duration,
            base_step=ceil(1 / self.smoothness),
        ):
            on_step(step)

    def _push_transition(self):
        self._transition(
            lambda step: self.state.update(
                {"x_position": self.state["x_position"] - step}
            )
        )

        self.state.update({"active_transition": None})
        logger.debug(f"push final state {self.state}")

    def _pop_transition(self):
        self._transition(
            lambda step: self.state.update(
                {"x_position": self.state["x_position"] + step}
            )
        )

        stack = self.state["stack"]
        self.remove_hotspot(stack.pop())
        self.state.update({"stack": stack, "active_transition": None})
        logger.debug(f"pop final state {self.state}")

    def push(self, Hotspot):
        if self.state["active_transition"] is not None:
            logger.debug(f"Currently transitioning, ignoring push of {Hotspot}")
            return

        logger.debug(f"Starting a new push transition with hotspot {Hotspot}")
        self.state.update(
            {
                "active_transition": "PUSH",
                "x_position": self.width,
                "stack": self.state["stack"] + [self.create_hotspot(Hotspot)],
            }
        )
        logger.debug(f"push initial state {self.state}")

        threading.Thread(target=self._push_transition).start()

    def pop(self):
        if self.state["active_transition"] is not None:
            logger.debug("Currently transitioning, ignoring pop")
            return

        if len(self.state["stack"]) == 1:
            logger.debug("Unable to pop last hotspot from stack, ignoring pop")
            return

        logger.debug("Starting a new pop transition")
        self.state.update(
            {
                "active_transition": "POP",
                "x_position": 0,
            }
        )
        logger.debug(f"push initial state {self.state}")

        threading.Thread(target=self._pop_transition).start()

    def render(self, image):
        x_position = self.state["x_position"]
        foreground_hotspot = self.state["stack"][-1]
        foreground_layer = foreground_hotspot.render(image)

        # if no active transition only the top hotspot needs to be rendered
        if not self.state["active_transition"] or len(self.state["stack"]) < 2:
            return foreground_layer

        # crop foreground so it can be offset to the right by x_position
        crop_boundaries = (0, 0, image.size[0] - x_position, image.size[1])
        cropped_foreground_layer = foreground_layer.crop(crop_boundaries)

        # render background layer and paste foreground offset to the right by x_position
        background_hotspot = self.state["stack"][-2]
        background_layer = background_hotspot.render(image)
        background_layer.paste(
            cropped_foreground_layer,
            (image.size[0] - cropped_foreground_layer.size[0], 0),
        )

        return background_layer


class PaginatedHotspot(Hotspot):
    transition_duration = 0.25
    smoothness = 1
    height = 0
    default_state = {
        "transition_progress": 0,
        "current_page": None,
        "previous_page": None,
        "active_transition": None,
    }

    def __init__(
        self,
        Pages,
        scrollbar_width=10,
        scrollbar_border_width=1,
        scrollbar_padding=3,
        initial_state={},
        **kwargs,
    ):
        assert len(Pages) > 0
        self.Pages = Pages

        super().__init__(
            **kwargs,
            initial_state={
                "scrollbar_y": 0,
                "scrollbar_width": scrollbar_width,
                "scrollbar_border_width": scrollbar_border_width,
                "scrollbar_padding": scrollbar_padding,
                **initial_state,
            },
        )
        self.state["current_page"] = self.create_hotspot(Pages[0])

    @property
    def current_page(self):
        return self.state["current_page"]

    @property
    def current_page_index(self):
        return self.Pages.index(type(self.current_page))

    def _scroll_transition(self):
        for step in transition(
            distance=self.height,
            duration=self.transition_duration,
            base_step=ceil(1 / self.smoothness),
        ):
            progress = self.state["transition_progress"]
            progress_step = step / self.height
            self.state.update({"transition_progress": progress + progress_step})

        self.remove_hotspot(self.state["previous_page"])
        self.state.update(
            {"transition_progress": 0, "active_transition": None, "previous_page": None}
        )

    def scroll(self, type):
        if self.state["active_transition"] is not None:
            logger.debug(f"{self} currently scrolling, ignoring {type} scroll")
            return

        current_index = self.current_page_index
        next_index = current_index - 1 if type == "UP" else current_index + 1

        if next_index < 0 or next_index >= len(self.Pages):
            logger.debug(f"{self} has no more pages, ignoring {type} scroll")
            return

        self.state.update(
            {
                "active_transition": type,
                "previous_page": self.state["current_page"],
                "current_page": self.create_hotspot(self.Pages[next_index]),
            }
        )

        threading.Thread(target=self._scroll_transition).start()

    def scroll_up(self):
        self.scroll("UP")

    def scroll_down(self):
        self.scroll("DOWN")

    def _get_scrollbar_y(self, bar_height):
        bar_y = int(self.current_page_index * self.height / len(self.Pages))

        # Offset the scrollbar according to transition progress.
        # Use the inverse of progress since offset decreases as it increases
        transition_progress = self.state["transition_progress"]

        if self.state["active_transition"] == "UP":
            return bar_y + int((1 - transition_progress) * bar_height)

        if self.state["active_transition"] == "DOWN":
            return bar_y - int((1 - transition_progress) * bar_height)

        return bar_y

    def _render_scrollbar(self, image):
        bar_padding = self.state["scrollbar_padding"]
        bar_height = int(image.height / len(self.Pages))
        bar_y = self._get_scrollbar_y(bar_height)

        ImageDraw.Draw(image).rectangle(
            (
                bar_padding,
                bar_y + bar_padding,
                image.size[0] - bar_padding,
                bar_y + bar_height - bar_padding,
            ),
            fill="white",
        )
        return image

    def _render_pages(self, image):
        current_page = self.state["current_page"]
        previous_page = self.state["previous_page"]
        active_transition = self.state["active_transition"]
        transition_progress = self.state["transition_progress"]

        # if no active transition only the current page should render
        current_page_layer = current_page.render(image)
        if not active_transition:
            return current_page_layer

        # if transition has not moved only the previous page should render since
        # the current page is being transitioned to
        previous_page_layer = previous_page.render(image)
        if active_transition and transition_progress == 0:
            return previous_page_layer

        if active_transition == "UP":
            # move y position down from top of image as transition progresses
            y_position = int(transition_progress * self.height)

            # if scrolling up the current_page moves down from the top
            # paste bottom of current page above the top of the previous page
            image.paste(
                current_page_layer.crop(
                    (0, image.size[1] - y_position, image.size[0], image.size[1])
                ),
                (0, 0),
            )
            image.paste(
                previous_page_layer.crop(
                    (0, 0, image.size[0], image.size[1] - y_position)
                ),
                (0, y_position),
            )
        else:
            # move y position up from bottom of image as transition progresses
            y_position = int((1 - transition_progress) * self.height)

            # if scrolling down the current_page moves up from the bottom
            # paste top of current page below the bottom of the previous page
            image.paste(
                previous_page_layer.crop(
                    (0, image.size[1] - y_position, image.size[0], image.size[1])
                ),
                (0, 0),
            )
            image.paste(
                current_page_layer.crop(
                    (0, 0, image.size[0], image.size[1] - y_position)
                ),
                (0, y_position),
            )

        return image

    def render(self, image):
        scrollbar_width = self.state["scrollbar_width"]
        border_width = self.state["scrollbar_border_width"]
        pages_width = image.width - scrollbar_width - border_width

        return apply_layers(
            image,
            [
                layer(
                    self._render_scrollbar,
                    size=(scrollbar_width - border_width, image.height),
                ),
                layer(
                    rectangle,
                    size=(border_width, image.height),
                    pos=(scrollbar_width, 0),
                ),
                layer(
                    self._render_pages,
                    size=(pages_width, image.height),
                    pos=(scrollbar_width + border_width, 0),
                ),
            ],
        )


class CornersHotspot(Hotspot):
    def render(self, image):
        draw = ImageDraw.Draw(image)
        draw.point((0, 0), fill="white")
        draw.point((0, image.size[1] - 1), fill="white")
        draw.point((image.size[0] - 1, 0), fill="white")
        draw.point((image.size[0] - 1, image.size[1] - 1), fill="white")
        return image
