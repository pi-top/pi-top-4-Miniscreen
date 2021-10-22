from dataclasses import dataclass, field
from typing import Dict, Type

from ...menu_base import MenuBase
from .menu_edge_behaviour import MenuEdgeBehaviour
from .page import PageConfig


@dataclass
class MenuConfig:
    menu_cls: Type[MenuBase]
    children: Dict[str, PageConfig] = field(default_factory=dict)
    parent_goes_to_first_page: bool = False
    top_edge: MenuEdgeBehaviour = MenuEdgeBehaviour.NONE
    bottom_edge: MenuEdgeBehaviour = MenuEdgeBehaviour.NONE
