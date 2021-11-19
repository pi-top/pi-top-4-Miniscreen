from typing import Dict

from ....hotspots.image_hotspot import Hotspot as ImageHotspot
from ....hotspots.text_hotspot import Hotspot as TextHotspot
from ...base import Page as PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config, image_path, text):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.image_path = image_path
        self.text = text
        self.setup_hotspots()

    def setup_hotspots(self):
        FONT_SIZE = 14
        ICON_SIZE = 25
        TEXT_LEFT_MARGIN = int(self.width * 0.3)
        ICON_LEFT_MARGIN = (TEXT_LEFT_MARGIN - ICON_SIZE) / 2

        self.hotspots: Dict = {
            (ICON_LEFT_MARGIN, self.vertical_middle_position(ICON_SIZE)): [
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=(ICON_SIZE, ICON_SIZE),
                    image_path=self.image_path,
                ),
            ],
            (TEXT_LEFT_MARGIN, self.vertical_middle_position(FONT_SIZE)): [
                TextHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=(self.width - TEXT_LEFT_MARGIN, FONT_SIZE),
                    text=self.text,
                    font_size=FONT_SIZE,
                    anchor="lt",
                    xy=(0, 0),
                )
            ],
        }
