from typing import Callable, Union

from ....hotspots.base import HotspotInstance
from ....hotspots.image_hotspot import Hotspot as ImageHotspot
from ....hotspots.text_hotspot import Hotspot as TextHotspot
from ....types import Coordinate
from ...base import Page as PageBase


class Page(PageBase):
    def __init__(
        self,
        size: Coordinate,
        image_path: str,
        text: Union[str, Callable],
        child_menu_cls=None,
    ) -> None:
        self.image_path = image_path
        self.text = text
        super().__init__(size=size, child_menu_cls=child_menu_cls)
        self.reset()

    def reset(self) -> None:
        FONT_SIZE = 14
        ICON_SIZE = 25
        TEXT_LEFT_MARGIN = int(self.width * 0.3)
        ICON_LEFT_MARGIN = int((TEXT_LEFT_MARGIN - ICON_SIZE) / 2)

        self.hotspot_instances = [
            HotspotInstance(
                ImageHotspot(
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=self.image_path,
                ),
                (ICON_LEFT_MARGIN, self.offset_pos_for_vertical_center(ICON_SIZE)),
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
