from __future__ import (
    annotations,  # PEP 563 postponed evaluations allows dataclass to have children of its own type
)

from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from ..menu_base import MenuBase
from ..pages.base import PageBase


@dataclass
class PageConfig:
    page_cls: Type[PageBase]
    child_menu: Optional[Dict] = field(default_factory=dict)


@dataclass
class MenuConfig:
    menu_cls: Type[MenuBase]
    children: Dict[str, PageConfig] = field(default_factory=dict)
    go_to_first: bool = False


@dataclass
class MenuAppConfig:
    children: Dict[str, MenuConfig] = field(default_factory=dict)
