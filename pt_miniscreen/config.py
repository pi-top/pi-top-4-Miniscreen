from __future__ import (
    annotations,  # PEP 563 postponed evaluations allows dataclass to have children of its own type
)

from dataclasses import dataclass, field
from types import ModuleType
from typing import Dict, List, Optional, Type

from .menu_base import MenuBase
from .pages import hud, settings, settings_connection  # , guide


@dataclass
class ActionConfig:
    type: str = ""
    icon: str = ""
    systemd_service: str = ""
    commands: List[str] = field(default_factory=list)


@dataclass
class PageConfig:
    page: ModuleType
    children: Dict[str, MenuConfig] = field(default_factory=dict)
    action: Optional[ActionConfig] = None


@dataclass
class MenuConfig:
    menu_cls: Type[MenuBase]
    children: Dict[str, PageConfig] = field(default_factory=dict)


menu_config = dict(
    [
        (
            "hud",
            MenuConfig(
                menu_cls=hud.Menu,
                children=dict(
                    [
                        ("battery", PageConfig(page=hud.battery)),
                        ("cpu", PageConfig(page=hud.cpu)),
                        ("wifi", PageConfig(page=hud.wifi)),
                        ("ethernet", PageConfig(page=hud.ethernet)),
                        ("ap", PageConfig(page=hud.ap)),
                        ("usb", PageConfig(page=hud.usb)),
                    ]
                ),
            ),
        ),
        (
            "settings",
            MenuConfig(
                menu_cls=settings.Menu,
                children=dict(
                    [
                        (
                            "settings.connection",
                            PageConfig(
                                page=settings.connection,
                                children=dict(
                                    [
                                        (
                                            "settings.connection.ssh",
                                            MenuConfig(
                                                menu_cls=settings_connection.Menu,
                                                children=dict(
                                                    [
                                                        (
                                                            "settings.connection.ssh.page",
                                                            PageConfig(
                                                                page=settings_connection.ssh,
                                                                action=ActionConfig(
                                                                    type="systemd_service",
                                                                    icon="ssh",
                                                                    systemd_service="ssh",
                                                                ),
                                                            ),
                                                        ),
                                                    ],
                                                ),
                                            ),
                                        ),
                                        #                 (
                                        #                     "settings.connection.vnc",
                                        #                     PageConfig(
                                        #                         page=settings.vnc,
                                        #                         action=ActionConfig(
                                        #                             type="systemd_service",
                                        #                             icon="vnc",
                                        #                             systemd_service="vnc",
                                        #                         ),
                                        #                     ),
                                        #                 ),
                                        #                 (
                                        #                     "settings.connection.further_link",
                                        #                     PageConfig(
                                        #                         page=settings.further_link,
                                        #                         action=ActionConfig(
                                        #                             type="systemd_service",
                                        #                             icon="further_link",
                                        #                             systemd_service="further-link",
                                        #                         ),
                                        #                     ),
                                        #                 ),
                                        #                 (
                                        #                     "settings.connection.further_link",
                                        #                     PageConfig(
                                        #                         page=settings.further_link,
                                        #                         action=ActionConfig(
                                        #                             type="systemd_service",
                                        #                             icon="further_link",
                                        #                             systemd_service="further-link",
                                        #                         ),
                                        #                     ),
                                        #                 ),
                                        #             ]
                                        #         ),
                                        #     ),
                                        # ),
                                        # (
                                        #     "settings.display",
                                        #     PageConfig(
                                        #         page=settings.display,
                                        #         children=dict(
                                        #             [
                                        #                 (
                                        #                     "settings.display.hdmi_reset",
                                        #                     PageConfig(
                                        #                         page=settings.ssh,
                                        #                         action=ActionConfig(
                                        #                             type="commands",
                                        #                             icon="hdmi_reset",
                                        #                             commands=[
                                        #                                 # Close 'Screen Layout Editor'
                                        #                                 'DISPLAY=:0 wmctrl -c "Screen Layout Editor"',
                                        #                                 # Reset all HDMI outputs to lowest common resolution
                                        #                                 "DISPLAY=:0 autorandr -c common",
                                        #                                 # Reset DPMS - show display if they were blanked
                                        #                                 "DISPLAY=:0 xset dpms force on",
                                        #                             ],
                                        #                         ),
                                        #                     ),
                                        #                 )
                                    ]
                                ),
                            ),
                        ),
                    ]
                ),
            ),
        ),
    ]
)
