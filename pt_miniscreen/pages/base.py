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

        menu_factory = ConfigFactory(size, mode, interval)
        self.child_menu = {}
        if config.child_menu:
            for name, config in config.child_menu.items():
                self.child_menu[name] = menu_factory.get(config)

    def on_select_press(self):
        # Only invoked if there is no child menu in config
        pass
