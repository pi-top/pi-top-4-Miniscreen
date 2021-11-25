class Page:
    def __init__(self, size, child_context_name=None):
        self._size = size
        self.child_context_name = child_context_name

        self.invert = False
        self.visible = True
        self.font_size = 14
        self.wrap = True

        golden_ratio = (1 + 5 ** 0.5) / 2
        self.long_section_width = int(self.width / golden_ratio)
        self.short_section_width = self.width - self.long_section_width

        self.hotspot_instances = list()

        self.reset()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        # Resize hotspots
        self.reset()

    def reset(self):
        pass

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

    def offset_pos_for_vertical_center(self, hotspot_height):
        return int((self.height - hotspot_height) / 2)
