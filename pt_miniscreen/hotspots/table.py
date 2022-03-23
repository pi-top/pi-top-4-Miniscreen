import logging
from functools import partial

from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.image import ImageHotspot
from pt_miniscreen.hotspots.marquee_text import MarqueeTextHotspot

logger = logging.getLogger(__name__)


def isint(value):
    type(value) == int


class Row(Hotspot):
    def __init__(self, column_widths=[], Columns=[], initial_state={}, **kwargs):
        assert len(column_widths) == len(Columns)

        super().__init__(
            **kwargs, initial_state={"column_widths": column_widths, **initial_state}
        )

        self.columns = [self.create_hotspot(Column) for Column in Columns]

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


class IconTextRow(Row):
    def __init__(
        self,
        text="",
        get_text=None,
        font_size=10,
        icon_path=None,
        icon_column_width=15,
        icon_vertical_align="center",
        text_vertical_align="center",
        text_align_rounding_fn=int,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            column_widths=[icon_column_width, "auto"],
            Columns=[
                partial(
                    ImageHotspot,
                    image_path=icon_path,
                    vertical_align=icon_vertical_align,
                ),
                partial(
                    MarqueeTextHotspot,
                    text=text,
                    get_text=get_text,
                    font_size=font_size,
                    vertical_align=text_vertical_align,
                    align_rounding_fn=text_align_rounding_fn,
                ),
            ],
        )

    # def render(self, image):
    #     if self.icon.image:
    #         icon_top = offset_to_center(image.height, self.icon.image.height)
    #         text_left = self.icon.image.width + self.state["icon_right_margin"]

    #         return apply_layers(image, [
    #             layer(self.icon.render, size=self.icon.image.size, pos=(0, icon_top)),
    #             layer(self.text.render, size=(image.width - text_left, image.height), pos=(text_left, 0))
    #         ])

    #     return self.text.render(image)


class TableHotspot(Hotspot):
    def __init__(self, Rows=[], row_gap=3, initial_state={}, **kwargs):
        super().__init__(**kwargs, initial_state={"row_gap": row_gap, **initial_state})

        self.rows = [self.create_hotspot(Row) for Row in Rows]

    def render(self, image):
        num_rows = len(self.rows)
        if num_rows == 0:
            return image

        row_gap = self.state["row_gap"]
        total_gap = max((num_rows - 1) * row_gap, 0)
        row_height = int((image.height - total_gap) / num_rows)

        return apply_layers(
            image,
            [
                layer(
                    row.render,
                    size=(image.width, row_height),
                    pos=(0, (row_height + row_gap) * row_index),
                )
                for (row_index, row) in enumerate(self.rows)
            ],
        )
