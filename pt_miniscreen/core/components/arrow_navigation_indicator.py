import logging
from enum import Enum, auto

from PIL import ImageDraw

from pt_miniscreen.core.component import Component
from pt_miniscreen.core.utils import apply_layers, layer

logger = logging.getLogger(__name__)


class ArrowPosition(Enum):
    TOP = auto()
    BOTTOM = auto()


class ArrowDrawing(Component):
    def __init__(self, position, visible, **kwargs):
        super().__init__(
            **kwargs,
            initial_state={
                "position": position,
                "visible": visible,
            },
        )

    def render(self, image):
        if self.state.get("position") == ArrowPosition.TOP and self.state["visible"]:
            ImageDraw.Draw(image).regular_polygon(((3, 3), 4), 3, fill=1)
        elif (
            self.state.get("position") == ArrowPosition.BOTTOM and self.state["visible"]
        ):
            ImageDraw.Draw(image).regular_polygon(
                ((3, image.size[1] - 4), 4),
                3,
                fill=1,
                rotation=180,
            )
        return image


class ArrowNavigationIndicator(Component):
    def __init__(
        self,
        upper_arrow_padding=(0, 0),
        lower_arrow_padding=(0, 0),
        top_arrow_visible=True,
        bottom_arrow_visible=True,
        **kwargs
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "upper_arrow_padding": upper_arrow_padding,
                "lower_arrow_padding": lower_arrow_padding,
            },
        )

        self.upper_arrow = self.create_child(
            ArrowDrawing, position=ArrowPosition.TOP, visible=top_arrow_visible
        )
        self.lower_arrow = self.create_child(
            ArrowDrawing,
            position=ArrowPosition.BOTTOM,
            visible=bottom_arrow_visible,
        )

    def render(self, image):
        layers = []
        arrow_size = (10, 10)

        if self.upper_arrow.state["visible"]:
            layers.append(
                layer(
                    self.upper_arrow.render,
                    size=arrow_size,
                    pos=self.state["upper_arrow_padding"],
                )
            )

        if self.lower_arrow.state["visible"]:
            icon_padding = self.state["lower_arrow_padding"]
            icon_pos = (icon_padding[0], image.height - arrow_size[1] - icon_padding[1])

            layers.append(layer(self.lower_arrow.render, size=arrow_size, pos=icon_pos))

        return apply_layers(image, layers)
