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
        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    # TODO: crop settings icon and re-position
                    # size=(self.short_section_width, size[1]),
                    size=self.size,
                    image_path=self.image_path,
                ),
            ],
            (int(self.width / 4), 0): [
                TextHotspot(
                    interval=self.interval,
                    mode=self.mode,
                    size=(self.width - int(self.width / 4), self.height),
                    text=self.text,
                    font_size=14,
                )
            ],
        }
