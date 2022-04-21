import logging
from functools import partial

from pt_miniscreen.core.component import Component
from pt_miniscreen.core.utils import apply_layers, arrow, layer

logger = logging.getLogger(__name__)


class ArrowNavigationIndicator(Component):
    def __init__(
        self,
        upper_arrow_padding=(0, 0),
        lower_arrow_padding=(0, 0),
        upper_arrow_visible=True,
        bottom_arrow_visible=True,
        **kwargs
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "upper_arrow_padding": upper_arrow_padding,
                "lower_arrow_padding": lower_arrow_padding,
                "upper_arrow_visible": upper_arrow_visible,
                "bottom_arrow_visible": bottom_arrow_visible,
            },
        )

    @property
    def upper_arrow_visible(self):
        return self.state["upper_arrow_visible"]

    @upper_arrow_visible.setter
    def upper_arrow_visible(self, value):
        self.state.update({"upper_arrow_visible": value})

    @property
    def bottom_arrow_visible(self):
        return self.state["bottom_arrow_visible"]

    @bottom_arrow_visible.setter
    def bottom_arrow_visible(self, value):
        self.state.update({"bottom_arrow_visible": value})

    def render(self, image):
        layers = []
        arrow_size = (10, 10)

        if self.upper_arrow_visible:
            layers.append(
                layer(
                    arrow,
                    size=arrow_size,
                    pos=self.state["upper_arrow_padding"],
                )
            )

        if self.bottom_arrow_visible:
            icon_padding = self.state["lower_arrow_padding"]
            icon_pos = (icon_padding[0], image.height - arrow_size[1] - icon_padding[1])

            layers.append(
                layer(partial(arrow, rotation=180), size=arrow_size, pos=icon_pos)
            )

        return apply_layers(image, layers)
