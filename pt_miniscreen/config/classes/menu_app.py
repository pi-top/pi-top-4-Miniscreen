from dataclasses import dataclass, field
from typing import Dict, Optional

from .menu import MenuTileConfig
from .title_bar import TitleBarConfig


@dataclass
class AppConfig:
    children: Dict[str, MenuTileConfig] = field(default_factory=dict)
    title_bar: Optional[TitleBarConfig] = None
