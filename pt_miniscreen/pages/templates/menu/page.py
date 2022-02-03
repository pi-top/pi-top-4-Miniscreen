from typing import Callable, Union

from ....hotspots.base import HotspotInstance
from ....hotspots.templates.image import Hotspot as ImageHotspot
from ....hotspots.templates.text import Hotspot as TextHotspot
from ....types import Coordinate
from ...base import Page as PageBase


class Page(PageBase):
    def __init__(
        self,
        size: Coordinate,
        image_path: str,
        text: Union[str, Callable],
        image_size=25,
        child_menu_cls=None,
    ) -> None:
        self.image_path = image_path
        self.image_size = image_size
        self.text = text
        super().__init__(size=size, child_menu_cls=child_menu_cls)
        self.reset()

    def reset(self) -> None:
        FONT_SIZE = 14
        TEXT_LEFT_MARGIN = int(self.width * 0.3)
        ICON_LEFT_MARGIN = int((TEXT_LEFT_MARGIN - self.image_size) / 2)

        self.hotspot_instances = [
            HotspotInstance(
                ImageHotspot(
                    size=(self.image_size, self.image_size),
                    image_path=self.image_path,
                ),
                (
                    ICON_LEFT_MARGIN,
                    self.offset_pos_for_vertical_center(self.image_size),
                ),
            ),
            HotspotInstance(
                TextHotspot(
                    size=(self.width - TEXT_LEFT_MARGIN, FONT_SIZE),
                    text=self.text,
                    font_size=FONT_SIZE,
                    anchor="lt",
                    xy=(0, 0),
                ),
                (TEXT_LEFT_MARGIN, self.offset_pos_for_vertical_center(FONT_SIZE)),
            ),
        ]
