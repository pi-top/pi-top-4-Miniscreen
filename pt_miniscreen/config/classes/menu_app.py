from dataclasses import dataclass, field
from typing import Dict

from .menu import MenuConfig


@dataclass
class MenuAppConfig:
    children: Dict[str, MenuConfig] = field(default_factory=dict)
