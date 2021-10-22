from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from ...pages.base import PageBase


@dataclass
class PageConfig:
    page_cls: Type[PageBase]
    child_menu: Optional[Dict] = field(default_factory=dict)
