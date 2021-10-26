from dataclasses import dataclass
from typing import Type

from ...pages.base import Page as PageBase


@dataclass
class TitleBarConfig:
    page_cls: Type[PageBase]
    height: int
