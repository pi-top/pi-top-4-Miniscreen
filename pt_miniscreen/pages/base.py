from ..config import ConfigFactory


class Page:
    def __init__(self, interval, size, mode, config, offset=(0, 0)):
        self.size = size
        self.mode = mode

        self.invert = False
        self.width = size[0]
        self.height = size[1]
        self.visible = True
        self.font_size = 14
        self.wrap = True

        golden_ratio = (1 + 5 ** 0.5) / 2
        self.long_section_width = int(self.width / golden_ratio)
        self.short_section_width = self.width - self.long_section_width

        config_factory = ConfigFactory(
            (size[0] + offset[0], size[1] + offset[1]), mode, interval, offset=(0, 0)
        )
        self.child_menu = dict()
        if config and config.child_menu:
            for menu_name, menu_config in config.child_menu.items():
                self.child_menu[menu_name] = config_factory.get(menu_config)

        self.hotspots = dict()

    def on_select_press(self):
        # Only invoked if there is no child menu in config
        pass

    def render(self, image):
        for position, hotspot_list in self.hotspots.items():
            for hotspot in hotspot_list:
                hotspot.paste_into(image, position)

    @property
    def interval(self):
        _interval = 1
        for position, hotspot_list in self.hotspots.items():
            for hotspot in hotspot_list:
                if hotspot.interval < _interval:
                    _interval = hotspot.interval

        return _interval
