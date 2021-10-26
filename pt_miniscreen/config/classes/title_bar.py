from dataclasses import dataclass
from typing import Type

from ...pages.base import PageBase


@dataclass
class TitleBarConfig:
    page_cls: Type[PageBase]
    height: int
