from dataclasses import dataclass
from typing import Optional, Type

from ...viewport import HotspotManager


@dataclass(eq=True)
class TitleBarBehaviour:
    text: Optional[str] = ""
    visible: Optional[bool] = True
    append_title: Optional[bool] = False
    height: Optional[int] = None


@dataclass
class TitleBarConfig:
    page_cls: Type[HotspotManager]
    behaviour: TitleBarBehaviour
