from typing import Dict

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.text_hotspot import Hotspot as TextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.hotspots: Dict = {
            (0, 0): [
                ImageHotspot(
                    interval=interval,
                    mode=mode,
                    # TODO: crop settings icon and re-position
                    # size=(self.short_section_width, size[1]),
                    size=size,
                    image_path=get_image_file_path("menu/settings.gif"),
                ),
            ],
            (int(self.width / 4), 0): [
                TextHotspot(
                    interval=interval,
                    mode=mode,
                    size=(self.width - int(self.width / 4), size[1]),
                    text="Connection",
                    font_size=14,
                )
            ],
        }
