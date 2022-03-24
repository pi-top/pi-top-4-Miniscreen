import logging
from functools import partial

from pt_miniscreen.core.components import Row
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.core.components.marquee_text import MarqueeText

logger = logging.getLogger(__name__)


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
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            column_widths=[icon_column_width, "auto"],
            Columns=[
                partial(
                    Image,
                    image_path=icon_path,
                    vertical_align=icon_vertical_align,
                ),
                partial(
                    MarqueeText,
                    text=text,
                    get_text=get_text,
                    font_size=font_size,
                    vertical_align=text_vertical_align,
                ),
            ],
        )
