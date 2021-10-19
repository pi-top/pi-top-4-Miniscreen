from .pages import hud, menu  # , guide

viewports = {
    "hud": {
        "module": hud,
        "children": {
            "battery": {"page": hud.battery},
            "cpu": {"page": hud.cpu},
            "wifi": {"page": hud.wifi},
            "ethernet": {"page": hud.ethernet},
            "ap": {"page": hud.ap},
            "usb": {"page": hud.usb},
        },
    },
    "settings": {
        "module": menu,
        "children": {
            "connection": {
                "page": menu.connection,
                "children": {
                    "ssh": {
                        "page": menu.ssh,
                        "action": {
                            "type": "systemd_service",
                            "icon": "ssh",
                            "systemd_service": "ssh",
                        },
                    },
                    "vnc": {
                        "page": menu.vnc,
                        "action": {
                            "type": "systemd_service",
                            "icon": "vnc",
                            "systemd_service": "vnc",
                        },
                    },
                    "further link": {
                        "page": menu.further_link,
                        "action": {
                            "type": "systemd_service",
                            "icon": "further_link",
                            "systemd_service": "further-link",
                        },
                    },
                },
            },
            "display": {
                "hdmi reset": {
                    "page": menu.hdmi_reset,
                    "action": {
                        "type": "commands",
                        "icon": "hdmi_reset",
                        "commands": [
                            # Close 'Screen Layout Editor'
                            'DISPLAY=:0 wmctrl -c "Screen Layout Editor"',
                            # Reset all HDMI outputs to lowest common resolution
                            "DISPLAY=:0 autorandr -c common",
                            # Reset DPMS - show display if they were blanked
                            "DISPLAY=:0 xset dpms force on",
                        ],
                    },
                },
                # "change resolution": {
                #   "page": change_resolution
                # },
            },
            # "power": {
            #   "safe power off": {
            #     "page": safe_power_off,
            #   },
            #   "reboot": {
            #     "page": reboot
            #   },
            # },
            # "help": {
            #     "guide": {
            #         "page": guide,
            #         "children": {
            #             "guide_page_1": {
            #                 "page": guide.page_1,
            #             },
            #             "guide_page_2": {
            #                 "page": guide.page_2,
            #             },
            #             "guide_page_3": {
            #                 "page": guide.page_3,
            #             },
            #         },
            #     },
            #     "links": {
            #         "page": links,
            #     },
            # },
        },
    },
}
