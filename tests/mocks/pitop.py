import io


class Button:
    def release(self):
        if hasattr(self, "when_released") and callable(self.when_released):
            self.when_released()


class Device:
    display_image = b""

    def display(self, image):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        self.display_image = img_byte_arr.getvalue()


class Miniscreen:
    size = (128, 64)
    is_active = False
    _contrast = 255

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_button = Button()
        self.select_button = Button()
        self.up_button = Button()
        self.down_button = Button()
        self.device = Device()

    def contrast(self, value):
        self._contrast = value


class Pitop:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.miniscreen = Miniscreen()
