from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from ...tiles import MenuTile
from .menu_edge_behaviour import MenuEdgeBehaviour
from .page import PageConfig
from .title_bar import TitleBarBehaviour


@dataclass
class MenuConfig:
    menu_cls: Type[MenuTile] = MenuTile
    children: Dict[str, PageConfig] = field(default_factory=dict)
    parent_goes_to_first_page: bool = True
    top_edge: MenuEdgeBehaviour = MenuEdgeBehaviour.NONE
    bottom_edge: MenuEdgeBehaviour = MenuEdgeBehaviour.NONE
    title_bar: Optional[TitleBarBehaviour] = None
