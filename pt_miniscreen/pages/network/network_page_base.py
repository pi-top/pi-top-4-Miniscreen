import logging
from dataclasses import dataclass
from math import floor
from typing import Any, Optional

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.image import Hotspot as ImageHotspot
from ...hotspots.templates.marquee_dynamic_text import (
    Hotspot as MarqueeDynamicTextHotspot,
)
from ...hotspots.templates.rectangle import Hotspot as RectangleHotspot
from ...hotspots.templates.text import Hotspot as TextHotspot
from ...state import Speeds
from ...types import Coordinate
from ...utils import get_image_file_path
from ..base import Page as PageBase

logger = logging.getLogger(__name__)


@dataclass
class RowDataGeneric:
    hotspot_type: Any
    icon_path: str = ""
    hotspot_size: Optional[Coordinate] = None


@dataclass
class RowDataText(RowDataGeneric):
    hotspot_type: Any = MarqueeDynamicTextHotspot
    text: str = ""


@dataclass
class NetworkPageData:
    first_row: Optional[RowDataGeneric] = None
    second_row: Optional[RowDataGeneric] = None
    third_row: Optional[RowDataGeneric] = None

    @property
    def rows(self):
        return [self.first_row, self.second_row, self.third_row]


class NetworkPageRowsLayout:
    MAX_ROWS = 3

    DEFAULT_FONT_SIZE = 10
    PADDING_TOP = 3
    PADDING_BOTTOM = 3
    PADDING_LEFT = 7
    PADDING_RIGHT = 7
    ROW_GAP = 3
    ICON_WIDTH = 11
    ICON_HEIGHT = 10
    ICON_RIGHT_MARGIN = 4

    icon_size = (ICON_WIDTH, ICON_HEIGHT)

    def __init__(self, size, pos):
        self.width = size[0]
        self.height = size[1]
        self.pos = pos

        ROWS_HEIGHT = self.height - self.PADDING_TOP - self.PADDING_BOTTOM
        self.ROW_HEIGHT = floor((ROWS_HEIGHT - self.ROW_GAP * 2) / 3)
        self.HOTSPOT_LEFT = self.PADDING_LEFT + self.ICON_WIDTH + self.ICON_RIGHT_MARGIN

    def row_top(self, index):
        return self.pos[1] + self.PADDING_TOP + (self.ROW_HEIGHT + self.ROW_GAP) * index

    def icon_position(self, index):
        assert 0 <= index < self.MAX_ROWS
        ICON_TOP = self.row_top(index) + int((self.ROW_HEIGHT - self.ICON_HEIGHT) / 2)
        return (self.PADDING_LEFT, ICON_TOP)

    def hotspot_position(self, index):
        assert 0 <= index < self.MAX_ROWS
        return (self.HOTSPOT_LEFT, self.row_top(index))

    def hotspot_size(self):
        return (self.width - self.HOTSPOT_LEFT - self.PADDING_RIGHT, self.ROW_HEIGHT)


class Page(PageBase):
    def __init__(self, size, title, row_data):
        self.title = title
        self.row_data = row_data
        super().__init__(size=size)
        self.reset()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        super().size = value

    def reset(self):
        self.hotspot_instances = list()

        HORIZONTAL_PADDING = 5
        TITLE_FONT_SIZE = 12
        UNDERLINE_THICKNESS = 1

        TITLE_LEFT = HORIZONTAL_PADDING
        TITLE_TOP_MARGIN = 1
        TITLE_BOTTOM_MARGIN = 2

        TITLE_POS = (TITLE_LEFT, TITLE_TOP_MARGIN)
        UNDERLINE_POS = (
            HORIZONTAL_PADDING,
            TITLE_POS[1] + TITLE_FONT_SIZE + TITLE_BOTTOM_MARGIN,
        )
        ROWS_POS = (0, UNDERLINE_POS[1] + UNDERLINE_THICKNESS)

        TITLE_SIZE = (self.size[0] - TITLE_POS[0] - HORIZONTAL_PADDING, TITLE_FONT_SIZE)
        UNDERLINE_SIZE = (self.size[0] - HORIZONTAL_PADDING * 2, UNDERLINE_THICKNESS)
        ROWS_SIZE = (self.size[0], self.size[1] - ROWS_POS[1])

        self.rows_layout_manager = NetworkPageRowsLayout(ROWS_SIZE, ROWS_POS)

        self.hotspot_instances.append(
            HotspotInstance(
                TextHotspot(
                    size=TITLE_SIZE,
                    text=self.title,
                    font_size=TITLE_FONT_SIZE,
                    align="center",
                ),
                TITLE_POS,
            )
        )

        self.hotspot_instances.append(
            HotspotInstance(RectangleHotspot(size=UNDERLINE_SIZE), UNDERLINE_POS)
        )

        for row_number, row_info in enumerate(self.row_data.rows):
            if row_info is None:
                continue
            for hotspot_instance in self._hotspot_instances_for_row(
                row_number, row_info
            ):
                self.hotspot_instances.append(hotspot_instance)

    def _hotspot_instances_for_row(self, row_number, row_data):
        hotspot_size = self.rows_layout_manager.hotspot_size()
        hotspot_position = self.rows_layout_manager.hotspot_position(row_number)

        has_icon = len(row_data.icon_path) > 0
        if not has_icon:
            hotspot_size = [
                hotspot_size[0]
                + self.rows_layout_manager.icon_size[0]
                + self.rows_layout_manager.icon_position(row_number)[0],
                hotspot_size[1]
                + self.rows_layout_manager.icon_size[1]
                + self.rows_layout_manager.icon_position(row_number)[1],
            ]
            hotspot_position = [
                self.rows_layout_manager.PADDING_LEFT,
                hotspot_position[1],
            ]

        if isinstance(row_data, RowDataText):
            content_hotspot = MarqueeDynamicTextHotspot(
                interval=Speeds.MARQUEE.value,
                size=hotspot_size,
                text=row_data.text,
                font_size=self.rows_layout_manager.DEFAULT_FONT_SIZE,
            )
        else:
            content_hotspot = row_data.hotspot_type(
                interval=Speeds.MARQUEE.value,
                size=hotspot_size,
            )

        hotspot_instances = [
            HotspotInstance(content_hotspot, hotspot_position),
        ]

        if has_icon:
            hotspot_instances.append(
                HotspotInstance(
                    ImageHotspot(
                        interval=Speeds.DYNAMIC_PAGE_REDRAW.value,
                        size=self.rows_layout_manager.icon_size,
                        image_path=get_image_file_path(row_data.icon_path),
                    ),
                    self.rows_layout_manager.icon_position(row_number),
                ),
            )

        return hotspot_instances
