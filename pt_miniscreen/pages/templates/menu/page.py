from typing import Dict

from ....hotspots.image_hotspot import Hotspot as ImageHotspot
from ....hotspots.text_hotspot import Hotspot as TextHotspot
from ...base import Page as PageBase


class Page(PageBase):
    def __init__(self, size, image_path, text):
        self.image_path = image_path
        self.text = text
        super().__init__(size=size)

    def reset(self):
        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    # TODO: crop settings icon and re-position
                    # size=(self.short_section_width, size[1]),
                    size=self.size,
                    image_path=self.image_path,
                ),
            ],
            (int(self.width / 4), 0): [
                TextHotspot(
                    size=(self.width - int(self.width / 4), self.height),
                    text=self.text,
                    font_size=14,
                )
            ],
        }
