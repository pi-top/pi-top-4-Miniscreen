class ConfigFactory:
    def __init__(self, size, mode):
        self.size = size
        self.mode = mode

    def get(self, config):
        # avoid circular import
        from .config import MenuTileConfig, PageConfig

        if isinstance(config, MenuTileConfig):
            return config.menu_cls(
                size=self.size,
                mode=self.mode,
                config=config,
            )
        elif isinstance(config, PageConfig):
            return config.page_cls(
                size=self.size,
                mode=self.mode,
                config=config,
            )
