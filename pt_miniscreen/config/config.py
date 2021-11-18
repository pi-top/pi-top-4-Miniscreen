from ..pages import hud, overlay, settings, settings_connection, settings_display
from .classes.menu import MenuConfig
from .classes.menu_app import MenuAppConfig
from .classes.page import PageConfig
from .classes.title_bar import TitleBarBehaviour, TitleBarConfig

# from .classes.menu_edge_behaviour import MenuEdgeBehaviour

menu_app_config = MenuAppConfig(
    title_bar=TitleBarConfig(
        page_cls=overlay.title_bar.TitleBar,
        behaviour=TitleBarBehaviour(height=19),
    ),
    children=dict(
        [
            (
                "hud",
                MenuConfig(
                    parent_goes_to_first_page=False,
                    title_bar=TitleBarBehaviour(visible=False),
                    children=dict(
                        [
                            (
                                "battery",
                                PageConfig(page_cls=hud.battery.Page),
                            ),
                            ("cpu", PageConfig(page_cls=hud.cpu.Page)),
                            ("wifi", PageConfig(page_cls=hud.wifi.Page)),
                            (
                                "ethernet",
                                PageConfig(page_cls=hud.ethernet.Page),
                            ),
                            ("ap", PageConfig(page_cls=hud.ap.Page)),
                            ("usb", PageConfig(page_cls=hud.usb.Page)),
                        ]
                    ),
                ),
            ),
            (
                "settings",
                MenuConfig(
                    title_bar=TitleBarBehaviour(
                        visible=True,
                        text="Settings",
                    ),
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
                                                    title_bar=TitleBarBehaviour(
                                                        text="Connection",
                                                        append_title=True,
                                                    ),
                                                    children=dict(
                                                        [
                                                            (
                                                                "settings_connection.ssh",
                                                                PageConfig(
                                                                    page_cls=settings_connection.ssh.Page,
                                                                ),
                                                            ),
                                                            (
                                                                "settings.connection.vnc",
                                                                PageConfig(
                                                                    page_cls=settings_connection.vnc.Page,
                                                                ),
                                                            ),
                                                            (
                                                                "settings.connection.further_link",
                                                                PageConfig(
                                                                    page_cls=settings_connection.further_link.Page,
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ),
                            (
                                "display",
                                PageConfig(
                                    page_cls=settings.display.Page,
                                    child_menu=dict(
                                        [
                                            (
                                                "settings.display",
                                                MenuConfig(
                                                    title_bar=TitleBarBehaviour(
                                                        text="Display",
                                                        append_title=True,
                                                    ),
                                                    children=dict(
                                                        [
                                                            (
                                                                "settings_display.hdmi_reset",
                                                                PageConfig(
                                                                    page_cls=settings_display.hdmi_reset.Page,
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ),
                        ]
                    ),
                ),
            ),
        ]
    ),
)
