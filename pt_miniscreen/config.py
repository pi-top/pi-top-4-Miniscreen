from __future__ import (
    annotations,  # PEP 563 postponed evaluations allows dataclass to have children of its own type
)

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from .menu_base import MenuBase
from .pages import hud, settings, settings_connection  # , guide
from .pages.base import PageBase


@dataclass
class ActionConfig:
    type: str = ""
    icon: str = ""
    systemd_service: str = ""
    commands: List[str] = field(default_factory=list)


@dataclass
class PageConfig:
    page_cls: Type[PageBase]
    child_menu: Optional[Dict] = field(default_factory=dict)
    # child_menu: Optional[Dict[str, MenuConfig]] = field(default_factory=dict)
    action: Optional[ActionConfig] = None


@dataclass
class MenuConfig:
    menu_cls: Type[MenuBase]
    children: Dict[str, PageConfig] = field(default_factory=dict)
    go_to_first: bool = False


@dataclass
class MenuAppConfig:
    children: Dict[str, MenuConfig] = field(default_factory=dict)


menu_app_config = MenuAppConfig(
    children=dict(
        [
            (
                "hud",
                MenuConfig(
                    menu_cls=hud.Menu,
                    children=dict(
                        [
                            ("battery", PageConfig(page_cls=hud.battery.Page)),
                            ("cpu", PageConfig(page_cls=hud.cpu.Page)),
                            ("wifi", PageConfig(page_cls=hud.wifi.Page)),
                            ("ethernet", PageConfig(page_cls=hud.ethernet.Page)),
                            ("ap", PageConfig(page_cls=hud.ap.Page)),
                            ("usb", PageConfig(page_cls=hud.usb.Page)),
                        ]
                    ),
                ),
            ),
            (
                "settings",
                MenuConfig(
                    menu_cls=settings.Menu,
                    go_to_first=True,
                    children=dict(
                        [
                            (
                                "connection",
                                PageConfig(
                                    page_cls=settings.connection.Page,
                                    child_menu=dict(
                                        [
                                            (
                                                "settings.connection",
                                                MenuConfig(
                                                    menu_cls=settings_connection.Menu,
                                                    children=dict(
                                                        [
                                                            (
                                                                "settings_connection.ssh",
                                                                PageConfig(
                                                                    page_cls=settings_connection.ssh.Page,
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
                                            #                         page_cls=settings.vnc.Page,
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
                                            #                         page_cls=settings.further_link.Page,
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
                                            #                         page_cls=settings.further_link.Page,
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
                                            #         page_cls=settings.display.Page,
                                            #         children=dict(
                                            #             [
                                            #                 (
                                            #                     "settings.display.hdmi_reset",
                                            #                     PageConfig(
                                            #                         page_cls=settings.ssh.Page,
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
)
