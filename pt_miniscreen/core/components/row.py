import logging

from ..component import Component
from ..utils import apply_layers, layer

logger = logging.getLogger(__name__)


def isint(value):
    isinstance(value, int)


class Row(Component):
    def __init__(self, column_widths=[], Columns=[], initial_state={}, **kwargs):
        assert len(column_widths) == len(Columns)

        super().__init__(
            **kwargs, initial_state={"column_widths": column_widths, **initial_state}
        )

        self.columns = [self.create_child(Column) for Column in Columns]

    def render(self, image):
        column_widths = self.state["column_widths"]

        known_width = sum(filter(isint, column_widths))
        num_autos = max(column_widths.count("auto"), 1)
        auto_width = max(int((image.width - known_width) / num_autos), 0)

        layers = []
        left_pos = 0
        for column_index, column in enumerate(self.columns):
            width = column_widths[column_index]
            if width == "auto":
                width = auto_width

            layers.append(
                layer(column.render, size=(width, image.height), pos=(left_pos, 0))
            )
            left_pos += width

        return apply_layers(image, layers)
