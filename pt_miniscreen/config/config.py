from ..pages import hud  # , settings, settings_connection, settings_display  # , guide
from .classes.menu import MenuConfig
from .classes.menu_app import MenuAppConfig
from .classes.menu_edge_behaviour import MenuEdgeBehaviour
from .classes.page import PageConfig

menu_app_config = MenuAppConfig(
    children=dict(
        [
            (
                "hud",
                MenuConfig(
                    menu_cls=hud.Menu,
                    top_edge=MenuEdgeBehaviour.NONE,
                    bottom_edge=MenuEdgeBehaviour.NONE,
                    children=dict(
                        [
                            ("battery", PageConfig(page_cls=hud.battery.Page)),
                            ("cpu", PageConfig(page_cls=hud.cpu.Page)),
                            # ("wifi", PageConfig(page_cls=hud.wifi.Page)),
                            # ("ethernet", PageConfig(page_cls=hud.ethernet.Page)),
                            # ("ap", PageConfig(page_cls=hud.ap.Page)),
                            # ("usb", PageConfig(page_cls=hud.usb.Page)),
                        ]
                    ),
                ),
            ),
            # (
            #     "settings",
            #     MenuConfig(
            #         menu_cls=settings.Menu,
            #         top_edge=MenuEdgeBehaviour.NONE,
            #         bottom_edge=MenuEdgeBehaviour.NONE,
            #         children=dict(
            #             [
            #                 (
            #                     "connection",
            #                     PageConfig(
            #                         page_cls=settings.connection.Page,
            #                         child_menu=dict(
            #                             [
            #                                 (
            #                                     "settings.connection",
            #                                     MenuConfig(
            #                                         menu_cls=settings_connection.Menu,
            #                                         top_edge=MenuEdgeBehaviour.NONE,
            #                                         bottom_edge=MenuEdgeBehaviour.NONE,
            #                                         children=dict(
            #                                             [
            #                                                 (
            #                                                     "settings_connection.ssh",
            #                                                     PageConfig(
            #                                                         page_cls=settings_connection.ssh.Page,
            #                                                     ),
            #                                                 ),
            #                                                 (
            #                                                     "settings.connection.vnc",
            #                                                     PageConfig(
            #                                                         page_cls=settings_connection.vnc.Page,
            #                                                     ),
            #                                                 ),
            #                                                 (
            #                                                     "settings.connection.further_link",
            #                                                     PageConfig(
            #                                                         page_cls=settings_connection.further_link.Page,
            #                                                     ),
            #                                                 ),
            #                                             ],
            #                                         ),
            #                                     ),
            #                                 ),
            #                             ]
            #                         ),
            #                     ),
            #                 ),
            #                 (
            #                     "display",
            #                     PageConfig(
            #                         page_cls=settings.display.Page,
            #                         child_menu=dict(
            #                             [
            #                                 (
            #                                     "settings.display",
            #                                     MenuConfig(
            #                                         menu_cls=settings_display.Menu,
            #                                         top_edge=MenuEdgeBehaviour.NONE,
            #                                         bottom_edge=MenuEdgeBehaviour.NONE,
            #                                         children=dict(
            #                                             [
            #                                                 (
            #                                                     "settings_display.hdmi_reset",
            #                                                     PageConfig(
            #                                                         page_cls=settings_display.hdmi_reset.Page,
            #                                                     ),
            #                                                 ),
            #                                             ],
            #                                         ),
            #                                     ),
            #                                 ),
            #                             ]
            #                         ),
            #                     ),
            #                 ),
            #             ]
            #         ),
            #     ),
            # ),
        ]
    )
)
