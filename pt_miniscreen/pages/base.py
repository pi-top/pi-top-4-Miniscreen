from ..config import ConfigFactory


# Based on luma.core hotspots/snapshots
class PageBase:
    def __init__(self, interval, size, mode, config):
        self.interval = interval
        self.size = size
        self.mode = mode

        self.last_updated = -self.interval
        self.invert = False
        self.width = size[0]
        self.height = size[1]
        self.visible = True
        self.font_size = 14
        self.wrap = True

        golden_ratio = (1 + 5 ** 0.5) / 2
        self.long_section_width = int(size[0] / golden_ratio)
        self.short_section_width = size[0] - self.long_section_width

        config_factory = ConfigFactory(size, mode, interval)

        self.child_menu = dict()
        if config and config.child_menu:
            for menu_name, menu_config in config.child_menu.items():
                self.child_menu[menu_name] = config_factory.get(menu_config)

    def on_select_press(self):
        # Only invoked if there is no child menu in config
        pass
