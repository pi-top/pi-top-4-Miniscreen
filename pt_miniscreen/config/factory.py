class ConfigFactory:
    def __init__(self, size, mode, redraw_speed, offset):
        self.size = size
        self.mode = mode
        self.redraw_speed = redraw_speed
        self.offset = offset

    def get(self, config):
        # avoid circular import
        from .config import MenuConfig, PageConfig

        if isinstance(config, MenuConfig):
            return config.menu_cls(
                size=self.size,
                mode=self.mode,
                redraw_speed=self.redraw_speed,
                config=config,
            )
        elif isinstance(config, PageConfig):
            return config.page_cls(
                interval=self.redraw_speed,
                size=self.size,
                mode=self.mode,
                config=config,
                offset=self.offset,
            )
