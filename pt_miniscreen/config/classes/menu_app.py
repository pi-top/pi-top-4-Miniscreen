from dataclasses import dataclass, field
from typing import Dict, Optional

from .menu import MenuConfig
from .title_bar import TitleBarConfig


@dataclass
class MenuAppConfig:
    children: Dict[str, MenuConfig] = field(default_factory=dict)
    title_bar: Optional[TitleBarConfig] = None
