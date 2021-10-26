import PIL.Image
import PIL.ImageDraw
from pitop.common.sys_info import get_network_strength

from ..utils import get_image_file_path
from .image_hotspot import Hotspot as ImageHotspot

wifi_images = {
    "no": PIL.Image.open(
        get_image_file_path("sys_info/networking/wifi_strength_bars/wifi_no_signal.png")
    ),
    "weak": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_weak_signal.png"
        )
    ),
    "okay": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_okay_signal.png"
        )
    ),
    "good": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_good_signal.png"
        )
    ),
    "excellent": PIL.Image.open(
        get_image_file_path(
            "sys_info/networking/wifi_strength_bars/wifi_excellent_signal.png"
        )
    ),
}


class Hotspot(ImageHotspot):
    def __init__(self, interval, size, mode, image_path, xy=None):
        super().__init__(interval, size, mode, image_path, xy)

    def render(self, image):
        wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100
        if wifi_strength <= 0:
            self.image = wifi_images["no"]
        elif wifi_strength <= 0.25:
            self.image = wifi_images["weak"]
        elif wifi_strength <= 0.5:
            self.image = wifi_images["okay"]
        elif wifi_strength <= 0.75:
            self.image = wifi_images["good"]
        else:
            self.image = wifi_images["excellent"]

        super().render(image)
