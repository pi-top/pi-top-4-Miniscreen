import io
from threading import Thread


class Button:
    def release(self):
        if hasattr(self, "when_released") and callable(self.when_released):
            t = Thread(target=self.when_released, args=(), daemon=True)
            t.start()

    def press(self):
        if hasattr(self, "when_pressed") and callable(self.when_pressed):
            t = Thread(target=self.when_pressed, args=(), daemon=True)
            t.start()


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
    device: Device
    cancel_button: Button
    select_button: Button
    up_button: Button
    down_button: Button

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_button = Button()
        self.select_button = Button()
        self.up_button = Button()
        self.down_button = Button()
        self.device = Device()

    def contrast(self, value):
        self._contrast = value

    def reset(self):
        pass
