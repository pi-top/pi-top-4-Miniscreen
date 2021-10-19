from __future__ import (
    annotations,  # PEP 563 postponed evaluations allows dataclass to have children of its own type
)

from dataclasses import dataclass
from types import ModuleType
from typing import Dict, List, Optional

from .pages import hud, settings  # , guide


@dataclass
class ActionConfig:
    type: str = ""
    icon: str = ""
    systemd_service: str = ""
    commands: List[str] = list()


@dataclass
class PageConfig:
    page: ModuleType
    children: Dict[str, PageConfig] = dict()
    action: Optional[ActionConfig] = None


@dataclass
class ViewportConfig:
    module: ModuleType
    children: Dict[str, PageConfig] = dict()


menu_config = dict(
    [
        (
            "hud",
            ViewportConfig(
                module=hud,
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
            ViewportConfig(
                module=settings,
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
                                            PageConfig(
                                                page=settings.ssh,
                                                action=ActionConfig(
                                                    type="systemd_service",
                                                    icon="ssh",
                                                    systemd_service="ssh",
                                                ),
                                            ),
                                        ),
                                        (
                                            "settings.connection.vnc",
                                            PageConfig(
                                                page=settings.vnc,
                                                action=ActionConfig(
                                                    type="systemd_service",
                                                    icon="vnc",
                                                    systemd_service="vnc",
                                                ),
                                            ),
                                        ),
                                        (
                                            "settings.connection.further_link",
                                            PageConfig(
                                                page=settings.further_link,
                                                action=ActionConfig(
                                                    type="systemd_service",
                                                    icon="further_link",
                                                    systemd_service="further-link",
                                                ),
                                            ),
                                        ),
                                        (
                                            "settings.connection.further_link",
                                            PageConfig(
                                                page=settings.further_link,
                                                action=ActionConfig(
                                                    type="systemd_service",
                                                    icon="further_link",
                                                    systemd_service="further-link",
                                                ),
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                        ),
                        (
                            "settings.display",
                            PageConfig(
                                page=settings.display,
                                children=dict(
                                    [
                                        (
                                            "settings.display.hdmi_reset",
                                            PageConfig(
                                                page=settings.ssh,
                                                action=ActionConfig(
                                                    type="commands",
                                                    icon="hdmi_reset",
                                                    commands=[
                                                        # Close 'Screen Layout Editor'
                                                        'DISPLAY=:0 wmctrl -c "Screen Layout Editor"',
                                                        # Reset all HDMI outputs to lowest common resolution
                                                        "DISPLAY=:0 autorandr -c common",
                                                        # Reset DPMS - show display if they were blanked
                                                        "DISPLAY=:0 xset dpms force on",
                                                    ],
                                                ),
                                            ),
                                        )
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
