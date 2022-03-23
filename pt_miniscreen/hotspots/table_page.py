from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.utils import apply_layers, layer, rectangle
from pt_miniscreen.hotspots.table import TableHotspot
from pt_miniscreen.hotspots.text import TextHotspot


class TablePageHotspot(Hotspot):
    def __init__(
        self,
        title,
        Rows,
        title_font_size=12,
        title_margin_bottom=2,
        underline_thickness=1,
        underline_margin_bottom=3,
        initial_state={},
        **kwargs
    ):
        super().__init__(
            **kwargs,
            initial_state={
                "title_margin_bottom": title_margin_bottom,
                "underline_thickness": underline_thickness,
                "underline_margin_bottom": underline_margin_bottom,
                **initial_state,
            }
        )

        self.title = self.create_hotspot(
            TextHotspot, text=title, font_size=title_font_size, align="center"
        )
        self.table = self.create_hotspot(TableHotspot, Rows=Rows)

    def render(self, image):
        padding_top = 1
        padding_bottom = 3
        title_margin_bottom = self.state["title_margin_bottom"]
        underline_thickness = self.state["underline_thickness"]
        underline_margin_bottom = self.state["underline_margin_bottom"]

        title_size = (image.width, self.title.state["font"].size)
        title_pos = (0, padding_top)

        underline_horizontal_padding = 4
        underline_top = title_pos[1] + title_size[1] + title_margin_bottom
        underline_size = (
            image.width - underline_horizontal_padding * 2,
            underline_thickness,
        )
        underline_pos = (underline_horizontal_padding, underline_top)

        table_horizontal_padding = 6
        table_top = underline_top + underline_size[1] + underline_margin_bottom
        table_size = (
            image.width - table_horizontal_padding * 2,
            image.height - table_top - padding_bottom,
        )
        table_pos = (table_horizontal_padding, table_top)

        return apply_layers(
            image,
            [
                layer(self.title.render, size=title_size, pos=title_pos),
                layer(rectangle, size=underline_size, pos=underline_pos),
                layer(self.table.render, size=table_size, pos=table_pos),
            ],
        )
