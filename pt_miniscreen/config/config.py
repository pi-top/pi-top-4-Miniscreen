from ..pages import hud, settings, settings_connection  # , guide
from .classes import MenuAppConfig, MenuConfig, PageConfig

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
                                                    go_to_first=True,
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
