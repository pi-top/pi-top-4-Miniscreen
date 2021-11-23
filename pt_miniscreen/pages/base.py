from ..config import ConfigFactory


class Page:
    def __init__(self, size, mode):
        self._size = size
        self.mode = mode

        self.invert = False
        self.visible = True
        self.font_size = 14
        self.wrap = True

        golden_ratio = (1 + 5 ** 0.5) / 2
        self.long_section_width = int(self.width / golden_ratio)
        self.short_section_width = self.width - self.long_section_width

        config_factory = ConfigFactory(size, mode)
        self.child_menu = dict()
        if config and config.child_menu:
            for menu_name, menu_config in config.child_menu.items():
                self.child_menu[menu_name] = config_factory.get(menu_config)

        self.hotspots = dict()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        # Resize hotspots
        self.setup_hotspots()
        # Resize childs
        for _, menu in self.child_menu.items():
            menu.size = self.size

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, value):
        self.size = (value, self.height)

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, value):
        self.size = (self.width, value)

    def on_select_press(self):
        # Only invoked if there is no child menu in config
        pass

    def setup_hotspots(self):
        pass

    # TODO: remove this function in favour of using viewport directly
    def render(self, image):
        for position, hotspot_list in self.hotspots.items():
            for hotspot in hotspot_list:
                hotspot.paste_into(image, position)

    def offset_pos_for_vertical_center(self, hotspot_height):
        return int((self.height - hotspot_height) / 2)
