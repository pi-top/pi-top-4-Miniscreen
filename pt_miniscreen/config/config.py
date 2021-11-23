from ..pages import hud, overlay, settings, settings_connection, settings_display
from .classes.menu import ScrollSelectorTileConfig
from .classes.menu_app import AppConfig
from .classes.page import PageConfig
from .classes.title_bar import TitleBarBehaviour, TitleBarConfig

# from .classes.menu_edge_behaviour import MenuEdgeBehaviour

app_config = AppConfig(
    children=[
        TileGroupConfig(
            menu=MenuTileConfig(
                children=[
                    PageConfig(page_cls=hud.battery.Page),
                    PageConfig(page_cls=hud.cpu.Page),
                    PageConfig(page_cls=hud.wifi.Page),
                    PageConfig(page_cls=hud.ethernet.Page),
                    PageConfig(page_cls=hud.ap.Page),
                    PageConfig(page_cls=hud.usb.Page),
                ]
            )
        ),
        TileGroupConfig(
            tiles=[
                TitleBarTileConfig(
                    rel_size=(1, 0.3),
                    rel_pos=(0, 0),
                    show_menu_name=True,
                    page=PageConfig(page_cls=hud.battery.Page),
                ),
                MenuTileConfig(
                    rel_size=(1, 0.7),
                    rel_pos=(0, 0.3),
                    menu=MenuConfig(
                        name="settings",
                        children=[
                            PageConfig(
                                page_cls=settings.connection.Page,
                                child_menu=MenuConfig(
                                    name="connection",
                                    children=[
                                        PageConfig(
                                            page_cls=settings_connection.ssh.Page
                                        ),
                                        PageConfig(
                                            page_cls=settings_connection.vnc.Page
                                        ),
                                        PageConfig(
                                            page_cls=settings_connection.further_link.Page
                                        ),
                                    ],
                                ),
                            ),
                            PageConfig(
                                page_cls=settings.display.Page,
                                child_menu=MenuConfig(
                                    name="display",
                                    children=[
                                        PageConfig(
                                            page_cls=settings_display.hdmi_reset.Page
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ]
        ),
    ]
)
