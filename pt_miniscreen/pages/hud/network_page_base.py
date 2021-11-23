from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple, Union

from pt_miniscreen.state import Speeds

from ...hotspots.image_hotspot import Hotspot as ImageHotspot
from ...hotspots.marquee_text_hotspot import Hotspot as MarqueeTextHotspot
from ...utils import get_image_file_path
from ..base import Page as PageBase


@dataclass
class RowDataGeneric:
    icon_path: str
    hotspot_type: Any
    hotspot_size: Union[Tuple[int, int], None] = None


@dataclass
class RowDataText(RowDataGeneric):
    hotspot_type: Any = MarqueeTextHotspot
    text: Union[str, Callable] = ""


@dataclass
class NetworkPageData:
    first_row: Union[RowDataGeneric, None] = None
    second_row: Union[RowDataGeneric, None] = None
    third_row: Union[RowDataGeneric, None] = None

    @property
    def rows(self):
        return [self.first_row, self.second_row, self.third_row]


class NetworkPageLayout:
    MAX_ROWS = 3

    DEFAULT_FONT_SIZE = 12
    ICON_X_POS = 10
    MARGIN_X_LEFT = 30
    MARGIN_X_RIGHT = 10
    ICON_WIDTH = 12
    ICON_HEIGHT = 12
    icon_size = (ICON_WIDTH, ICON_HEIGHT)
    VERTICAL_SPACING = 4
    ROW_HEIGHT = ICON_HEIGHT + VERTICAL_SPACING

    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]

        self.SCALE = self.height / 64.0
        self.DELTA_Y = int(self.ROW_HEIGHT * self.SCALE)
        self.COMMON_FIRST_LINE_Y = int(10 * self.SCALE)

    def icon_position(self, index):
        assert 0 <= index < self.MAX_ROWS
        return (self.ICON_X_POS, self.COMMON_FIRST_LINE_Y + self.DELTA_Y * index)

    def hotspot_position(self, index):
        assert 0 <= index < self.MAX_ROWS
        return (self.MARGIN_X_LEFT, self.COMMON_FIRST_LINE_Y + self.DELTA_Y * index - 1)

    def hotspot_size(self):
        return (self.width - self.MARGIN_X_LEFT - self.MARGIN_X_RIGHT, self.ROW_HEIGHT)


class Page(PageBase):
    def __init__(self, size, row_data):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.row_data = row_data
        self.layout_manager = NetworkPageLayout(self.size)
        self.reset()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        super().size = value
        self.layout_manager = NetworkPageLayout(self.size)

    def reset(self):
        hotspot_instances = list()
        for row_number, row_info in enumerate(self.row_data.rows):
            if row_info is None:
                continue
            for hotspot_instance in self._hotspot_instances_for_row(
                row_number, row_info
            ):
                hotspot_instances.append(hotspot_instance)

        self.set_hotspot_instances(hotspot_instances, start=True)

    def _hotspot_instances_for_row(self, row_number, row_data):
        if isinstance(row_data, RowDataText):
            content_hotspot = MarqueeTextHotspot(
                interval=Speeds.MARQUEE.value,
                mode=self.mode,
                size=row_data.hotspot_size
                if row_data.hotspot_size
                else self.layout_manager.hotspot_size(),
                text=row_data.text,
                font_size=self.layout_manager.DEFAULT_FONT_SIZE,
            )
        else:
            content_hotspot = row_data.hotspot_type(
                interval=Speeds.MARQUEE.value,
                mode=self.mode,
                size=row_data.hotspot_size
                if row_data.hotspot_size
                else self.layout_manager.hotspot_size(),
            )

        image_hotspot = ImageHotspot(
            interval=self.interval,
            mode=self.mode,
            size=self.layout_manager.icon_size,
            image_path=get_image_file_path(row_data.icon_path),
        )

        return [
            HotspotInstance(
                image_hotspot, self.layout_manager.icon_position(row_number)
            ),
            HotspotInstance(
                content_hotspot, self.layout_manager.hotspot_position(row_number)
            ),
        ]
